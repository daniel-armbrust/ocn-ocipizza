#!/usr/bin/env bash

# Aplica os recursos Kubernetes do pizza-service e executa o bootstrap opcional
# responsável por preparar dados iniciais e configurações do serviço.

set -euo pipefail

# Variáveis globais

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DEPLOYMENT_MANIFEST="${SCRIPT_DIR}/deployment.yaml"
SERVICE_MANIFEST="${SCRIPT_DIR}/service.yaml"
BOOTSTRAP_SCRIPT="${SCRIPT_DIR}/bootstrap.sh"

# Funções

# Verifica se um arquivo obrigatório existe e não está vazio.
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

# Aplica o Deployment e o Service do pizza-service no cluster Kubernetes.
apply_resources() {
  require_manifest "$DEPLOYMENT_MANIFEST"
  require_manifest "$SERVICE_MANIFEST"
  require_environment_variables

  command -v envsubst >/dev/null 2>&1 || {
    echo "Erro: o comando 'envsubst' não está instalado ou não está no PATH." >&2
    exit 1
  }

  echo "Aplicando o Deployment do pizza-service..."
  envsubst '${REGISTRY} ${OCI_NAMESPACE}' < "$DEPLOYMENT_MANIFEST" \
    | kubectl apply --filename -

  echo "Aplicando o Service do pizza-service..."
  kubectl apply --filename "$SERVICE_MANIFEST"
}

# Executa o bootstrap do pizza-service quando o script estiver disponível.
run_bootstrap() {
  if [[ ! -f "$BOOTSTRAP_SCRIPT" ]]; then
    echo "Bootstrap não encontrado; ignorando: ${BOOTSTRAP_SCRIPT}"
    return 0
  fi

  echo "Executando o bootstrap do pizza-service..."
  bash "$BOOTSTRAP_SCRIPT"
}

# Fluxo principal

command -v kubectl >/dev/null 2>&1 || {
  echo "Erro: o comando 'kubectl' não está instalado ou não está no PATH." >&2
  exit 1
}

apply_resources
run_bootstrap

exit 0
