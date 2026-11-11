#!/usr/bin/env bash

# Remove o OCI Native Ingress Controller instalado como programa standalone.
# O fluxo também remove o namespace do controlador e o Cert-Manager instalado
# pelo script de deployment.

set -euo pipefail

# Variáveis globais

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
NATIVE_INGRESS_NAMESPACE="native-ingress-controller-system"
RELEASE_NAME="oci-native-ingress-controller"
CERT_MANAGER_MANIFEST="https://github.com/jetstack/cert-manager/releases/latest/download/cert-manager.yaml"
INGRESS_MANIFEST="${SCRIPT_DIR}/Ingress.yaml"
INGRESS_CLASS_MANIFEST="${SCRIPT_DIR}/IngressClass.yaml"
INGRESS_CLASS_PARAMETERS_MANIFEST="${SCRIPT_DIR}/IngressClassParameters.yaml"

# Funções

# Exibe a forma de uso do script.
usage() {
  cat <<'EOF'
 ██████╗  ██████╗██╗    ██████╗ ██╗███████╗███████╗ █████╗
██╔═══██╗██╔════╝██║    ╚══██╔╝██║╚══███╔╝╚══███╔╝██╔══██╗
██║   ██║██║     ██║      ██║  ██║  ███╔╝   ███╔╝ ███████║
██║   ██║██║     ██║      ██║  ██║ ███╔╝   ███╔╝  ██╔══██║
╚██████╔╝╚██████╗██║      ██║  ██║███████╗███████╗██║  ██║
 ╚═════╝  ╚═════╝╚═╝      ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝

   OCI Pizza - by Daniel Armbrust (darmbrust@gmail.com)

Uso: ./undeploy-standalone.sh

O script remove as regras de Ingress, o release Helm do OCI Native Ingress
Controller, o namespace native-ingress-controller-system e o Cert-Manager
instalado pelo deployment.
EOF
}

# Verifica se Helm e kubectl estão disponíveis antes da remoção.
check_dependencies() {
  local command_name

  for command_name in helm kubectl; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
      echo "Erro: o comando '${command_name}' não está instalado ou não está no PATH." >&2
      exit 1
    fi
  done
}

# Remove o release Helm caso ele ainda esteja registrado no cluster.
uninstall_controller() {
  if helm status "$RELEASE_NAME" \
    --namespace "$NATIVE_INGRESS_NAMESPACE" >/dev/null 2>&1; then
    echo "Removendo o release Helm do OCI Native Ingress Controller..."
    
    helm uninstall "$RELEASE_NAME" --namespace "$NATIVE_INGRESS_NAMESPACE"
  else
    echo "O release Helm não está instalado; continuando."
  fi
}

# Remove as regras antes do controlador para permitir a limpeza do Load Balancer.
delete_ingress_resources() {
  local manifest_path

  for manifest_path in \
    "$INGRESS_MANIFEST" \
    "$INGRESS_CLASS_MANIFEST" \
    "$INGRESS_CLASS_PARAMETERS_MANIFEST"; do
    
    if [[ -f "$manifest_path" ]]; then
      echo "Excluindo os recursos definidos em $(basename "$manifest_path")..."
      kubectl delete --filename "$manifest_path" --ignore-not-found
    fi

  done
}

# Exclui o namespace criado para os recursos do controlador.
delete_controller_namespace() {
  echo "Excluindo o namespace ${NATIVE_INGRESS_NAMESPACE}..."
  kubectl delete namespace "$NATIVE_INGRESS_NAMESPACE" --ignore-not-found
}

# Remove o Cert-Manager usando o mesmo manifesto aplicado no deployment.
delete_cert_manager() {
  echo "Removendo o Cert-Manager..."
  kubectl delete --filename "$CERT_MANAGER_MANIFEST" --ignore-not-found
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
delete_ingress_resources
uninstall_controller
delete_controller_namespace
delete_cert_manager

echo "OCI Native Ingress Controller standalone removido com sucesso."

exit 0