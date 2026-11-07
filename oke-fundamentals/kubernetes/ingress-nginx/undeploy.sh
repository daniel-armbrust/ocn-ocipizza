#!/usr/bin/env bash

# Remove o ingress-nginx usando o mesmo manifesto oficial utilizado na
# instalação via kubectl.
# Instalação baseada em: https://kubernetes.github.io/ingress-nginx/deploy/

set -euo pipefail

# Variáveis globais

INGRESS_NGINX_MANIFEST="https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.15.1/deploy/static/provider/cloud/deploy.yaml"

# Funções

# Remove os recursos do ingress-nginx aplicados pelo manifesto oficial.
undeploy_ingress_nginx() {
  echo "Removendo os recursos do ingress-nginx..."
  kubectl delete --filename "$INGRESS_NGINX_MANIFEST"
}

# Fluxo principal

undeploy_ingress_nginx

exit 0
