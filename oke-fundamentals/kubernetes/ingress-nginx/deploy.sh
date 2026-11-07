#!/usr/bin/env bash

# Instala o ingress-nginx usando o manifesto oficial aplicado diretamente pelo
# kubectl.
# Instalação baseada em: https://kubernetes.github.io/ingress-nginx/deploy/

set -euo pipefail

# Variáveis globais

INGRESS_NGINX_MANIFEST="https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.15.1/deploy/static/provider/cloud/deploy.yaml"

# Funções

# Aplica o manifesto oficial do ingress-nginx no cluster atual.
deploy_ingress_nginx() {
  echo "Aplicando o manifesto do ingress-nginx..."
  kubectl apply --filename "$INGRESS_NGINX_MANIFEST"
}

# Fluxo principal

deploy_ingress_nginx

exit 0
