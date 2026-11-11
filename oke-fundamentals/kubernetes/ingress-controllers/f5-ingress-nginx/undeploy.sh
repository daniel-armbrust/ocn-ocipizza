#!/usr/bin/env bash

# Remove o F5 NGINX Ingress Controller usando os mesmos manifestos oficiais
# aplicados durante a instalação.
# Instalação baseada no Quick Start:
# https://github.com/nginx/kubernetes-ingress#quick-start

set -euo pipefail

# Variáveis globais

NGINX_INGRESS_VERSION="v5.7.0"
NGINX_INGRESS_MANIFEST_BASE="https://raw.githubusercontent.com/nginx/kubernetes-ingress/${NGINX_INGRESS_VERSION}"

NGINX_INGRESS_MANIFESTS=(
  "${NGINX_INGRESS_MANIFEST_BASE}/deployments/common/ingress-class.yaml"
  "${NGINX_INGRESS_MANIFEST_BASE}/deployments/service/loadbalancer.yaml"
  "${NGINX_INGRESS_MANIFEST_BASE}/deployments/deployment/nginx-ingress.yaml"
  "${NGINX_INGRESS_MANIFEST_BASE}/deployments/common/nginx-config.yaml"
  "${NGINX_INGRESS_MANIFEST_BASE}/deployments/rbac/rbac.yaml"
  "${NGINX_INGRESS_MANIFEST_BASE}/deployments/common/ns-and-sa.yaml"
  "${NGINX_INGRESS_MANIFEST_BASE}/deploy/crds.yaml"
)

# Funções

# Remove os manifestos oficiais em ordem reversa à instalação.
undeploy_f5_nginx_ingress() {
  local manifest

  for manifest in "${NGINX_INGRESS_MANIFESTS[@]}"; do
    echo "Removendo os recursos definidos em ${manifest}..."
    kubectl delete --ignore-not-found --filename "$manifest"
  done
}

# Fluxo principal

undeploy_f5_nginx_ingress

exit 0
