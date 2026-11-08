#!/usr/bin/env bash

# Remove o ingress-nginx usando o mesmo manifesto oficial utilizado na
# instalação via kubectl.
# Instalação baseada em: https://kubernetes.github.io/ingress-nginx/deploy/

set -euo pipefail

# Variáveis globais

INGRESS_NGINX_MANIFEST="https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.15.1/deploy/static/provider/cloud/deploy.yaml"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
INGRESS_MANIFEST="${SCRIPT_DIR}/ingress.yaml"
INGRESS_SERVICE_MANIFEST="${SCRIPT_DIR}/service.yaml"

# Funções

# Remove os recursos do ingress-nginx aplicados pelo manifesto oficial.
undeploy_ingress_nginx() {
  # Remove as regras da aplicação e a configuração do Service antes de remover
  # o controlador.
  echo "Excluindo as regras de Ingress do OCI PIZZA..."
  kubectl delete --filename "$INGRESS_MANIFEST" --ignore-not-found
  kubectl delete --filename "$INGRESS_SERVICE_MANIFEST" --ignore-not-found

  echo "Removendo os recursos do ingress-nginx..."
  kubectl delete --filename "$INGRESS_NGINX_MANIFEST" --ignore-not-found
}

# Fluxo principal

undeploy_ingress_nginx

exit 0
