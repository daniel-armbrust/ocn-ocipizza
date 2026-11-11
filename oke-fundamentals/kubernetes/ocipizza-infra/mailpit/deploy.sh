#!/usr/bin/env bash

# Aplica o Deployment e o Service do Mailpit no namespace de infraestrutura.

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

# Aplica o Deployment e o Service do Mailpit no cluster Kubernetes.
apply_resources() {
  require_manifest "$DEPLOYMENT_MANIFEST"
  require_manifest "$SERVICE_MANIFEST"

  echo "Aplicando o Deployment do Mailpit..."
  kubectl apply --filename "$DEPLOYMENT_MANIFEST"

  echo "Aplicando o Service do Mailpit..."
  kubectl apply --filename "$SERVICE_MANIFEST"
}

# Fluxo principal

command -v kubectl >/dev/null 2>&1 || {
  echo "Erro: o comando 'kubectl' não está instalado ou não está no PATH." >&2
  exit 1
}

apply_resources

exit 0
