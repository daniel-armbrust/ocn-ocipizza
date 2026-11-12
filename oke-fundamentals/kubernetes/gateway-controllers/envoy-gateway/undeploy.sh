#!/usr/bin/env bash

# Remove o Envoy Gateway Controller, os recursos do Gateway API do OCI Pizza
# e os CRDs padrão instalados pelo script de deployment.

set -euo pipefail

# Variáveis globais

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
GATEWAY_API_MANIFEST="https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.2.0/standard-install.yaml"
ENVOY_GATEWAY_RELEASE="eg"
ENVOY_GATEWAY_NAMESPACE="envoy-gateway-system"
OCI_ENVOY_PROXY_MANIFEST="${SCRIPT_DIR}/oci-envoy-proxy.yaml"
GATEWAY_CLASS_MANIFEST="${SCRIPT_DIR}/oci-gateway-class.yaml"
GATEWAY_MANIFEST="${SCRIPT_DIR}/ocipizza-gateway.yaml"
SERVICES_HTTP_ROUTE_MANIFEST="${SCRIPT_DIR}/ocipizza-services-httproute.yaml"
INFRA_HTTP_ROUTE_MANIFEST="${SCRIPT_DIR}/ocipizza-infra-httproute.yaml"

# Funções

# Exibe a forma de uso e o propósito do script.
usage() {
  cat <<'EOF'
 ██████╗  ██████╗██╗    ██████╗ ██╗███████╗███████╗ █████╗
██╔═══██╗██╔════╝██║    ██╔══██╗██║╚══███╔╝╚══███╔╝██╔══██╗
██║   ██║██║     ██║    ██████╔╝██║  ███╔╝   ███╔╝ ███████║
██║   ██║██║     ██║    ██╔═══╝ ██║ ███╔╝   ███╔╝  ██╔══██║
╚██████╔╝╚██████╗██║    ██║     ██║███████╗███████╗██║  ██║
 ╚═════╝  ╚═════╝╚═╝    ╚═╝     ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝

   OCI Pizza - by Daniel Armbrust (darmbrust@gmail.com)

Uso: ./undeploy.sh

O script remove as rotas, o Gateway, o Envoy Gateway Controller, o namespace
do controlador e os CRDs padrão da Gateway API instalados pelo deployment.
EOF
}

# Verifica se os binários necessários estão disponíveis no PATH.
check_dependencies() {
  local command_name

  for command_name in kubectl helm; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
      echo "Erro: o comando '${command_name}' não está instalado ou não está no PATH." >&2
      exit 1
    fi
  done
}

# Verifica se os manifestos locais usados para a remoção existem.
check_manifests() {
  local manifest_path

  for manifest_path in \
    "$OCI_ENVOY_PROXY_MANIFEST" \
    "$GATEWAY_CLASS_MANIFEST" \
    "$GATEWAY_MANIFEST" \
    "$SERVICES_HTTP_ROUTE_MANIFEST" \
    "$INFRA_HTTP_ROUTE_MANIFEST"; do

    if [[ ! -f "$manifest_path" ]]; then
      echo "Erro: manifesto não encontrado: ${manifest_path}" >&2
      exit 1
    fi

  done
}

# Remove as rotas antes dos recursos parent e do controlador.
delete_http_routes() {
  echo "Excluindo as rotas da infraestrutura..."
  kubectl delete --filename "$INFRA_HTTP_ROUTE_MANIFEST" --ignore-not-found

  echo "Excluindo as rotas dos serviços OCI Pizza..."
  kubectl delete --filename "$SERVICES_HTTP_ROUTE_MANIFEST" --ignore-not-found
}

# Remove o Gateway, o GatewayClass e a configuração do proxy OCI.
delete_gateway_resources() {
  echo "Excluindo o Gateway do OCI Pizza..."
  kubectl delete --filename "$GATEWAY_MANIFEST" --ignore-not-found

  echo "Excluindo o GatewayClass..."
  kubectl delete --filename "$GATEWAY_CLASS_MANIFEST" --ignore-not-found

  echo "Excluindo a configuração do proxy Envoy..."
  kubectl delete --filename "$OCI_ENVOY_PROXY_MANIFEST" --ignore-not-found
}

# Remove o release Helm do Envoy Gateway quando ele estiver instalado.
uninstall_envoy_gateway() {
  if helm status "$ENVOY_GATEWAY_RELEASE" \
    --namespace "$ENVOY_GATEWAY_NAMESPACE" >/dev/null 2>&1; then
    echo "Removendo o release Helm do Envoy Gateway..."
    helm uninstall "$ENVOY_GATEWAY_RELEASE" \
      --namespace "$ENVOY_GATEWAY_NAMESPACE"
  else
    echo "O release Helm do Envoy Gateway não está instalado; continuando."
  fi
}

# Exclui o namespace criado para o controlador Envoy Gateway.
delete_controller_namespace() {
  echo "Excluindo o namespace ${ENVOY_GATEWAY_NAMESPACE}..."
  kubectl delete namespace "$ENVOY_GATEWAY_NAMESPACE" --ignore-not-found
}

# Remove os CRDs padrão da Gateway API instalados pelo script de deployment.
delete_gateway_api() {
  echo "Excluindo os CRDs padrão da Gateway API..."
  kubectl delete --filename "$GATEWAY_API_MANIFEST" --ignore-not-found
}

# Execução principal

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

if [[ "$#" -ne 0 ]]; then
  echo "Erro: argumento não reconhecido: $1" >&2
  usage >&2
  exit 1
fi

check_dependencies
check_manifests
delete_http_routes
delete_gateway_resources
uninstall_envoy_gateway
delete_controller_namespace
delete_gateway_api

echo "Envoy Gateway do OCI Pizza removido com sucesso."

exit 0