#!/usr/bin/env bash

# Instala o ingress-nginx usando o manifesto oficial aplicado diretamente pelo
# kubectl.
# Instalação baseada em: https://kubernetes.github.io/ingress-nginx/deploy/

set -euo pipefail

# Variáveis globais

INGRESS_NGINX_MANIFEST="https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.15.1/deploy/static/provider/cloud/deploy.yaml"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
INGRESS_MANIFEST="${SCRIPT_DIR}/ingress.yaml"
INGRESS_SERVICE_MANIFEST="${SCRIPT_DIR}/service.yaml"
INGRESS_NGINX_NAMESPACE="ingress-nginx"
INGRESS_NGINX_TIMEOUT="180s"

# Funções

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
  kubectl apply --filename "$INGRESS_NGINX_MANIFEST"

  # Aplica o Service do controlador com as annotations do Load Balancer OCI.
  echo "Aplicando o Service do ingress-nginx..."
  kubectl apply --filename "$INGRESS_SERVICE_MANIFEST"

  wait_for_ingress_nginx

  # Aplica as regras de Ingress do OCI PIZZA.
  echo "Aplicando as regras de Ingress do OCI PIZZA..."
  kubectl apply --filename "$INGRESS_MANIFEST"
}

# Fluxo principal

deploy_ingress_nginx

exit 0
