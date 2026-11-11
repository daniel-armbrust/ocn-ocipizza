#!/usr/bin/env bash

# Prepara os dados do order-service e aplica seus recursos Kubernetes.
# O bootstrap é executado antes do Deployment para garantir que o backend
# NoSQL e a mensageria estejam preparados antes da criação dos Pods.

set -euo pipefail

# Variáveis globais

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_MANIFEST="${SCRIPT_DIR}/deployment.yaml"
SERVICE_MANIFEST="${SCRIPT_DIR}/service.yaml"
BOOTSTRAP_SCRIPT="${SCRIPT_DIR}/bootstrap.sh"

# Funções

# Verifica se um manifesto obrigatório existe e não está vazio.
require_manifest() {
  local manifest="$1"

  if [[ ! -s "$manifest" ]]; then
    echo "Erro: manifesto obrigatório não encontrado ou vazio: ${manifest}" >&2
    exit 1
  fi
}

# Verifica as variáveis utilizadas para renderizar a imagem privada do OCIR.
require_environment_variables() {
  if [[ -z "${REGISTRY:-}" ]]; then
    echo "Erro: a variável de ambiente REGISTRY deve ser definida." >&2
    exit 1
  fi

  if [[ -z "${OCI_NAMESPACE:-}" ]]; then
    echo "Erro: a variável de ambiente OCI_NAMESPACE deve ser definida." >&2
    exit 1
  fi
}

# Executa o bootstrap do order-service quando o script estiver disponível.
run_bootstrap() {
  if [[ ! -f "$BOOTSTRAP_SCRIPT" ]]; then
    echo "Bootstrap não encontrado; ignorando: ${BOOTSTRAP_SCRIPT}"
    return 0
  fi

  echo "Executando o bootstrap do order-service..."
  bash "$BOOTSTRAP_SCRIPT"
}

# Aplica o Deployment renderizado e o Service do order-service no cluster.
apply_resources() {
  require_manifest "$DEPLOYMENT_MANIFEST"
  require_manifest "$SERVICE_MANIFEST"
  require_environment_variables

  command -v envsubst >/dev/null 2>&1 || {
    echo "Erro: o comando 'envsubst' não está instalado ou não está no PATH." >&2
    exit 1
  }

  echo "Aplicando o Deployment do order-service..."
  envsubst '${REGISTRY} ${OCI_NAMESPACE}' < "$DEPLOYMENT_MANIFEST" \
    | kubectl apply --filename -

  echo "Aplicando o Service do order-service..."
  kubectl apply --filename "$SERVICE_MANIFEST"
}

# Fluxo principal

command -v kubectl >/dev/null 2>&1 || {
  echo "Erro: o comando 'kubectl' não está instalado ou não está no PATH." >&2
  exit 1
}

run_bootstrap
apply_resources
