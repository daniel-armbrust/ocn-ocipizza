#!/usr/bin/env bash

# Exclui os recursos Kubernetes do frontend-service.
# O service.yaml é mantido somente para demonstração e não faz parte deste
# fluxo operacional.

set -euo pipefail

# Variáveis globais

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
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

# Exclui o Deployment do frontend-service sem falhar caso já tenha sido
# removido anteriormente.
delete_resources() {
  require_manifest "$DEPLOYMENT_MANIFEST"

  echo "Excluindo o Deployment do frontend-service..."
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
