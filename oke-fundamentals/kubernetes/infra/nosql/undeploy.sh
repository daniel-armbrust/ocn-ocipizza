#!/usr/bin/env bash

# Exclui o Deployment e o Service do Oracle NoSQL no namespace de infraestrutura.

set -euo pipefail

# Variáveis globais

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_MANIFEST="${SCRIPT_DIR}/deployment.yaml"
SERVICE_MANIFEST="${SCRIPT_DIR}/service.yaml"

# Funções

# Verifica se um manifesto obrigatório existe e não está vazio.
require_manifest() {
  local manifest="$1"

  if [[ ! -s "$manifest" ]]; then
    echo "Erro: manifesto obrigatório não encontrado ou vazio: ${manifest}" >&2
    exit 1
  fi
}

# Exclui o Service e o Deployment do NoSQL sem falhar se já não existirem.
delete_resources() {
  require_manifest "$SERVICE_MANIFEST"
  require_manifest "$DEPLOYMENT_MANIFEST"

  echo "Excluindo o Service do NoSQL..."
  kubectl delete \
    --filename "$SERVICE_MANIFEST" \
    --ignore-not-found

  echo "Excluindo o Deployment do NoSQL..."
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
