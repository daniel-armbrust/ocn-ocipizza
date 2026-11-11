#!/usr/bin/env bash

# Instala o F5 NGINX Ingress Controller usando os manifestos oficiais
# aplicados diretamente pelo kubectl.
# Instalação baseada no Quick Start:
# https://github.com/nginx/kubernetes-ingress#quick-start

set -euo pipefail

# Variáveis globais

NGINX_INGRESS_VERSION="v5.7.0"
NGINX_INGRESS_MANIFEST_BASE="https://raw.githubusercontent.com/nginx/kubernetes-ingress/${NGINX_INGRESS_VERSION}"
NGINX_INGRESS_IMAGE="docker.io/nginx/nginx-ingress:${NGINX_INGRESS_VERSION#v}"

NGINX_INGRESS_MANIFESTS=(
  "${NGINX_INGRESS_MANIFEST_BASE}/deploy/crds.yaml"
  "${NGINX_INGRESS_MANIFEST_BASE}/deployments/common/ns-and-sa.yaml"
  "${NGINX_INGRESS_MANIFEST_BASE}/deployments/rbac/rbac.yaml"
  "${NGINX_INGRESS_MANIFEST_BASE}/deployments/common/nginx-config.yaml"
  "${NGINX_INGRESS_MANIFEST_BASE}/deployments/deployment/nginx-ingress.yaml"
  "${NGINX_INGRESS_MANIFEST_BASE}/deployments/service/loadbalancer.yaml"
  "${NGINX_INGRESS_MANIFEST_BASE}/deployments/common/ingress-class.yaml"
)

# Funções

# Aplica os manifestos oficiais na ordem recomendada pelo Quick Start.
deploy_f5_nginx_ingress() {
  local manifest

  for manifest in "${NGINX_INGRESS_MANIFESTS[@]}"; do
    echo "Aplicando o manifesto ${manifest}..."

    if [[ "$manifest" == */deployments/deployment/nginx-ingress.yaml ]]; then
      # O manifesto oficial usa um nome curto. A imagem totalmente qualificada
      # evita o erro de nomes ambíguos no runtime dos workers Oracle Linux.
      curl --fail --silent --show-error --location "$manifest" \
        | sed "s#nginx/nginx-ingress:${NGINX_INGRESS_VERSION#v}#${NGINX_INGRESS_IMAGE}#g" \
        | kubectl apply --filename -
    else
      kubectl apply --filename "$manifest"
    fi
  done
}

# Fluxo principal

deploy_f5_nginx_ingress

exit 0
