#!/usr/bin/env bash

# Exclui os recursos Kubernetes do user-service.
# O script remove o Service e o Deployment, mas preserva o Secret JWT e os
# demais recursos utilizados pelo bootstrap do serviço.

set -euo pipefail

# Variáveis globais

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_MANIFEST="${SCRIPT_DIR}/service.yaml"
DEPLOYMENT_MANIFEST="${SCRIPT_DIR}/deployment.yaml"

# Funções

# Verifica se um manifesto obrigatório existe e não está vazio.
require_manifest() {
  local manifest="$1"

  if [[ ! -s "$manifest" ]]; then
    echo "Erro: manifesto não encontrado ou vazio: ${manifest}" >&2
    exit 1
  fi
}

# Exclui o Service e o Deployment do user-service sem falhar caso já tenham
# sido removidos anteriormente.
delete_resources() {
  require_manifest "$SERVICE_MANIFEST"
  require_manifest "$DEPLOYMENT_MANIFEST"

  echo "Excluindo o Service do user-service..."
  kubectl delete \
    --filename "$SERVICE_MANIFEST" \
    --ignore-not-found

  echo "Excluindo o Deployment do user-service..."
  kubectl delete \
    --filename "$DEPLOYMENT_MANIFEST" \
    --ignore-not-found
}

# Fluxo principal

command -v kubectl >/dev/null 2>&1 || {
  echo "Erro: o comando 'kubectl' não está instalado ou não está no PATH." >&2
  exit 1
}

delete_resources

exit 0