#!/usr/bin/env bash

# Remove o ingress-nginx usando o mesmo manifesto oficial utilizado na
# instalação via kubectl.
# Instalação baseada em: https://kubernetes.github.io/ingress-nginx/deploy/

set -euo pipefail

# Variáveis globais

INGRESS_NGINX_MANIFEST="https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.15.1/deploy/static/provider/cloud/deploy.yaml"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SERVICES_INGRESS_MANIFEST="${SCRIPT_DIR}/ocipizza-services-ingress.yaml"
INFRA_INGRESS_MANIFEST="${SCRIPT_DIR}/ocipizza-infra-ingress.yaml"
INGRESS_SERVICE_MANIFEST="${SCRIPT_DIR}/service.yaml"

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

O script remove as regras de Ingress, o Service do controlador e os recursos
do ingress-nginx aplicados pelo manifesto oficial.
EOF
}

# Verifica se o kubectl está disponível no PATH.
check_dependencies() {
  if ! command -v kubectl >/dev/null 2>&1; then
    echo "Erro: o comando 'kubectl' não está instalado ou não está no PATH." >&2
    exit 1
  fi
}

# Verifica se os manifestos locais de Service e Ingress existem.
check_manifests() {
  local manifest_path

  for manifest_path in \
    "$INGRESS_SERVICE_MANIFEST" \
    "$SERVICES_INGRESS_MANIFEST" \
    "$INFRA_INGRESS_MANIFEST"; do
    if [[ ! -f "$manifest_path" ]]; then
      echo "Erro: manifesto não encontrado: ${manifest_path}" >&2
      exit 1
    fi
  done
}

# Remove os recursos do ingress-nginx aplicados pelo manifesto oficial.
undeploy_ingress_nginx() {
  # Remove as regras da aplicação e a configuração do Service antes de remover
  # o controlador.
  echo "Excluindo as regras de Ingress do OCI PIZZA..."
  kubectl delete --filename "$SERVICES_INGRESS_MANIFEST" --ignore-not-found
  kubectl delete --filename "$INFRA_INGRESS_MANIFEST" --ignore-not-found
  kubectl delete --filename "$INGRESS_SERVICE_MANIFEST" --ignore-not-found

  echo "Removendo os recursos do ingress-nginx..."
  kubectl delete --filename "$INGRESS_NGINX_MANIFEST" --ignore-not-found
}

# Fluxo principal

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
undeploy_ingress_nginx

exit 0
