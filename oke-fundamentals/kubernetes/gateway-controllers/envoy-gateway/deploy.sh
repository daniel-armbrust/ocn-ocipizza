#!/usr/bin/env bash

# Instala o Gateway API e o Envoy Gateway Controller no OKE.
# A instalação utiliza os manifestos oficiais da Gateway API e o chart Helm
# oficial do Envoy Gateway. Em seguida, aplica a integração com o Load Balancer
# OCI e as rotas do OCI Pizza.

set -euo pipefail

# Variáveis globais

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
GATEWAY_API_MANIFEST="https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.2.0/standard-install.yaml"
ENVOY_GATEWAY_CHART="oci://docker.io/envoyproxy/gateway-helm"
ENVOY_GATEWAY_CHART_VERSION="v1.6.3"
ENVOY_GATEWAY_RELEASE="eg"
ENVOY_GATEWAY_NAMESPACE="envoy-gateway-system"
ENVOY_GATEWAY_TIMEOUT="90s"
GATEWAY_ADDRESS_TIMEOUT_SECONDS=180
GATEWAY_ADDRESS_POLL_INTERVAL_SECONDS=5
GATEWAY_NAME="ocipizza-envoy-gateway"
GATEWAY_NAMESPACE="default"
OCI_ENVOY_PROXY_MANIFEST="${SCRIPT_DIR}/oci-envoy-proxy.yaml"
GATEWAY_CLASS_MANIFEST="${SCRIPT_DIR}/oci-gateway-class.yaml"
GATEWAY_MANIFEST="${SCRIPT_DIR}/ocipizza-gateway.yaml"
SERVICES_HTTP_ROUTE_MANIFEST="${SCRIPT_DIR}/ocipizza-services-httproute.yaml"
INFRA_HTTP_ROUTE_MANIFEST="${SCRIPT_DIR}/ocipizza-infra-httproute.yaml"

# Funções

# Exibe a forma de uso e as etapas executadas pelo script.
usage() {
  cat <<'EOF'
 ██████╗  ██████╗██╗    ██████╗ ██╗███████╗███████╗ █████╗
██╔═══██╗██╔════╝██║    ██╔══██╗██║╚══███╔╝╚══███╔╝██╔══██╗
██║   ██║██║     ██║    ██████╔╝██║  ███╔╝   ███╔╝ ███████║
██║   ██║██║     ██║    ██╔═══╝ ██║ ███╔╝   ███╔╝  ██╔══██║
╚██████╔╝╚██████╗██║    ██║     ██║███████╗███████╗██║  ██║
 ╚═════╝  ╚═════╝╚═╝    ╚═╝     ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝

   OCI Pizza - by Daniel Armbrust (darmbrust@gmail.com)

Uso: ./deploy.sh

O script instala a Gateway API, o Envoy Gateway Controller, a integração
com o Load Balancer OCI e as rotas do OCI Pizza.
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

# Verifica se todos os manifestos locais necessários existem.
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

# Instala os CRDs padrão da Gateway API e aguarda o CRD principal ficar pronto.
install_gateway_api() {
  echo "Instalando os CRDs padrão da Gateway API..."
  kubectl apply --filename "$GATEWAY_API_MANIFEST"

  echo "Aguardando o CRD Gateway API ficar disponível..."
  kubectl wait \
    --for=condition=Established \
    crd/gateways.gateway.networking.k8s.io \
    --timeout "$ENVOY_GATEWAY_TIMEOUT"

  kubectl get crd gateways.gateway.networking.k8s.io
}

# Instala ou atualiza o Envoy Gateway Controller pelo chart OCI oficial.
install_envoy_gateway() {
  echo "Instalando o Envoy Gateway Controller via Helm..."
  helm upgrade --install "$ENVOY_GATEWAY_RELEASE" \
    "$ENVOY_GATEWAY_CHART" \
    --version "$ENVOY_GATEWAY_CHART_VERSION" \
    --namespace "$ENVOY_GATEWAY_NAMESPACE" \
    --create-namespace

  echo "Aguardando o Envoy Gateway Controller..."
  kubectl wait \
    --namespace "$ENVOY_GATEWAY_NAMESPACE" \
    --for=condition=Ready pod \
    --selector='control-plane=envoy-gateway' \
    --timeout "$ENVOY_GATEWAY_TIMEOUT"
}

# Aplica a configuração do proxy Envoy com as annotations do Load Balancer OCI.
apply_oci_integration() {
  echo "Aplicando a integração do Envoy Gateway com o Load Balancer OCI..."
  kubectl apply --filename "$OCI_ENVOY_PROXY_MANIFEST"
}

# Aplica os recursos Gateway API na ordem necessária para o roteamento.
apply_gateway_resources() {
  echo "Aplicando o GatewayClass..."
  kubectl apply --filename "$GATEWAY_CLASS_MANIFEST"

  echo "Aplicando o Gateway do OCI Pizza..."
  kubectl apply --filename "$GATEWAY_MANIFEST"

  echo "Aplicando as rotas dos serviços OCI Pizza..."
  kubectl apply --filename "$SERVICES_HTTP_ROUTE_MANIFEST"

  echo "Aplicando as rotas da infraestrutura..."
  kubectl apply --filename "$INFRA_HTTP_ROUTE_MANIFEST"
}

# Aguarda o Gateway receber o endereço público e o exibe ao final da instalação.
show_gateway_address() {
  local elapsed=0
  local gateway_address=""

  echo "Aguardando o endereço público do Gateway..."

  while (( elapsed < GATEWAY_ADDRESS_TIMEOUT_SECONDS )); do
    gateway_address="$(kubectl get gateway "$GATEWAY_NAME" \
      --namespace "$GATEWAY_NAMESPACE" \
      --output=jsonpath='{.status.addresses[0].value}' 2>/dev/null || true)"

    if [[ -n "$gateway_address" ]]; then
      echo "Gateway ${GATEWAY_NAME} disponível em: ${gateway_address}"
      return 0
    fi

    sleep "$GATEWAY_ADDRESS_POLL_INTERVAL_SECONDS"
    elapsed=$((elapsed + GATEWAY_ADDRESS_POLL_INTERVAL_SECONDS))
  done

  echo "Aviso: o Gateway ainda não recebeu um endereço dentro do tempo esperado." >&2
  kubectl get gateway "$GATEWAY_NAME" \
    --namespace "$GATEWAY_NAMESPACE" \
    --output wide >&2 || true
  return 0
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
install_gateway_api
install_envoy_gateway
apply_oci_integration
apply_gateway_resources
show_gateway_address

echo "Envoy Gateway do OCI Pizza instalado com sucesso."

exit 0