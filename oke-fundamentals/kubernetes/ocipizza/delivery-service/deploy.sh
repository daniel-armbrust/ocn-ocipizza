#!/usr/bin/env bash

# Aplica os recursos Kubernetes do delivery-service.
# Caso um bootstrap seja adicionado futuramente, ele será executado antes da
# criação dos Pods para preparar as dependências do serviço.

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

# Executa o bootstrap do delivery-service quando o script estiver disponível.
run_bootstrap() {
  if [[ ! -f "$BOOTSTRAP_SCRIPT" ]]; then
    echo "Bootstrap não encontrado; ignorando: ${BOOTSTRAP_SCRIPT}"
    return 0
  fi

  echo "Executando o bootstrap do delivery-service..."
  bash "$BOOTSTRAP_SCRIPT"
}

# Renderiza e aplica o Deployment e aplica o Service do delivery-service.
apply_resources() {
  require_manifest "$DEPLOYMENT_MANIFEST"
  require_manifest "$SERVICE_MANIFEST"
  require_environment_variables

  command -v envsubst >/dev/null 2>&1 || {
    echo "Erro: o comando 'envsubst' não está instalado ou não está no PATH." >&2
    exit 1
  }

  echo "Aplicando o Deployment do delivery-service..."
  envsubst '${REGISTRY} ${OCI_NAMESPACE}' < "$DEPLOYMENT_MANIFEST" \
    | kubectl apply --filename -

  echo "Aplicando o Service do delivery-service..."
  kubectl apply --filename "$SERVICE_MANIFEST"
}

# Fluxo principal

command -v kubectl >/dev/null 2>&1 || {
  echo "Erro: o comando 'kubectl' não está instalado ou não está no PATH." >&2
  exit 1
}

run_bootstrap
apply_resources

exit 0