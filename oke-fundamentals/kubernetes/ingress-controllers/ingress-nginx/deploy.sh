#!/usr/bin/env bash

# Instala o ingress-nginx usando o manifesto oficial aplicado diretamente pelo
# kubectl.
# Instalação baseada em: https://kubernetes.github.io/ingress-nginx/deploy/

set -euo pipefail

# Variáveis globais

INGRESS_NGINX_MANIFEST="https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.15.1/deploy/static/provider/cloud/deploy.yaml"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SERVICES_INGRESS_MANIFEST="${SCRIPT_DIR}/ocipizza-services-ingress.yaml"
INFRA_INGRESS_MANIFEST="${SCRIPT_DIR}/ocipizza-infra-ingress.yaml"
INGRESS_SERVICE_MANIFEST="${SCRIPT_DIR}/service.yaml"
INGRESS_NGINX_NAMESPACE="ingress-nginx"
INGRESS_NGINX_TIMEOUT="180s"

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

Uso: ./deploy.sh

O script instala o ingress-nginx usando o manifesto oficial aplicado via
kubectl e aplica as regras de Ingress dos serviços e da infraestrutura.
EOF
}

# Verifica se os binários necessários estão disponíveis no PATH.
check_dependencies() {
  local command_name

  for command_name in kubectl curl awk; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
      echo "Erro: o comando '${command_name}' não está instalado ou não está no PATH." >&2
      exit 1
    fi
  done
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

# Aplica o manifesto oficial com o gerenciamento de regras de segurança
# desabilitado antes de o Service LoadBalancer ser criado pelo OCI CCM.
apply_official_manifest() {
  curl --fail --silent --show-error --location "$INGRESS_NGINX_MANIFEST" \
    | awk '
      /^kind: Service$/ { in_controller_service = 1 }
      in_controller_service && /^  name: ingress-nginx-controller$/ {
        print
        print "  annotations:"
        print "    service.beta.kubernetes.io/oci-load-balancer-security-list-management-mode: \"None\""
        next
      }
      in_controller_service && /^---$/ { in_controller_service = 0 }
      { print }
    ' \
    | kubectl apply --filename -
}

# Aguarda o controlador e o certificado do admission webhook ficarem prontos.
wait_for_ingress_nginx() {
  echo "Aguardando o controlador ingress-nginx..."

  kubectl rollout status deployment/ingress-nginx-controller \
    --namespace "$INGRESS_NGINX_NAMESPACE" \
    --timeout "$INGRESS_NGINX_TIMEOUT"

  for admission_job in \
    ingress-nginx-admission-create \
    ingress-nginx-admission-patch; do
    # Jobs concluídos podem ser removidos automaticamente pelo cluster.
    if kubectl get job "$admission_job" \
      --namespace "$INGRESS_NGINX_NAMESPACE" >/dev/null 2>&1; then
      
      kubectl wait --for=condition=complete \
        "job/$admission_job" \
        --namespace "$INGRESS_NGINX_NAMESPACE" \
        --timeout "$INGRESS_NGINX_TIMEOUT"
    fi
  done
}

# Aplica o manifesto oficial do ingress-nginx no cluster atual.
deploy_ingress_nginx() {
  echo "Aplicando o manifesto do ingress-nginx..."
  apply_official_manifest

  # Aplica o Service do controlador com as annotations do Load Balancer OCI.
  echo "Aplicando o Service do ingress-nginx..."
  kubectl apply --filename "$INGRESS_SERVICE_MANIFEST"

  wait_for_ingress_nginx

  # Aplica as regras de Ingress do OCI PIZZA.
  echo "Aplicando as regras de Ingress dos serviços OCI PIZZA..."
  kubectl apply --filename "$SERVICES_INGRESS_MANIFEST"

  echo "Aplicando as regras de Ingress da infraestrutura..."
  kubectl apply --filename "$INFRA_INGRESS_MANIFEST"
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
deploy_ingress_nginx

exit 0
