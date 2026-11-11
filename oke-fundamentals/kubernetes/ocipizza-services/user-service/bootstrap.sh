#!/usr/bin/env bash

# Prepara os dados do user-service no MySQL do laboratório e cria o Secret
# Kubernetes que disponibiliza o par de chaves utilizado pelos tokens JWT.
# O port-forward é temporário e encerrado ao finalizar o bootstrap.

set -euo pipefail

# Variáveis globais

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# A estrutura posiciona este script três níveis abaixo de oke-fundamentals:
# kubernetes/ocipizza-services/user-service/.
OKE_FUNDAMENTALS_DIR="$(cd -- "${SCRIPT_DIR}/../../.." && pwd)"
REPOSITORY_DIR="$(cd -- "${OKE_FUNDAMENTALS_DIR}/.." && pwd)"
USER_SERVICE_DIR="${REPOSITORY_DIR}/services/user-service"
USER_SERVICE_BOOTSTRAP="${USER_SERVICE_DIR}/bootstrap.sh"
JWT_PRIVATE_KEY_FILE="${USER_SERVICE_DIR}/secrets/jwt_private_key.pem"
JWT_PUBLIC_KEY_FILE="${USER_SERVICE_DIR}/secrets/jwt_public_key.pem"

INFRA_NAMESPACE="${INFRA_NAMESPACE:-ocipizza-infra}"
SERVICE_NAMESPACE="${SERVICE_NAMESPACE:-ocipizza-services}"
JWT_SECRET_NAME="${JWT_SECRET_NAME:-user-service-jwt}"
# O bootstrap original do user-service utiliza localhost:13306 para o MySQL.
MYSQL_LOCAL_PORT="13306"
MYSQL_REMOTE_PORT="${MYSQL_REMOTE_PORT:-3306}"
PORT_FORWARD_TIMEOUT_SECONDS="${PORT_FORWARD_TIMEOUT_SECONDS:-30}"

MYSQL_POD_NAME=""
PORT_FORWARD_PIDS=()

# Funções

# Exibe um título visual para identificar cada etapa executada pelo script.
display_step() {
  local message="$1"

  printf '\n### %s ###\n\n' "$message"
}

# Encerra todos os processos de port-forward iniciados durante o bootstrap.
cleanup_port_forwards() {
  local pid

  for pid in "${PORT_FORWARD_PIDS[@]}"; do
    if kill -0 "$pid" >/dev/null 2>&1; then
      kill "$pid" >/dev/null 2>&1 || true
      wait "$pid" 2>/dev/null || true
    fi
  done
}

# Aguarda uma porta local aceitar conexões e detecta falhas ou timeout do
# processo de port-forward correspondente.
wait_for_local_port() {
  local port="$1"
  local process_id="$2"
  local description="$3"
  local elapsed_seconds=0

  while ! (echo >/dev/tcp/127.0.0.1/"$port") >/dev/null 2>&1; do
    if ! kill -0 "$process_id" >/dev/null 2>&1; then
      echo "Erro: o port-forward para ${description} foi encerrado." >&2
      return 1
    fi

    if ((elapsed_seconds >= PORT_FORWARD_TIMEOUT_SECONDS)); then
      echo "Erro: timeout ao aguardar ${description} na porta ${port}." >&2
      return 1
    fi

    sleep 1
    ((elapsed_seconds += 1))
  done
}

# Localiza o Pod em execução do MySQL independentemente de ele ter sido criado
# diretamente, por ReplicationController ou por ReplicaSet.
resolve_mysql_pod_name() {
  MYSQL_POD_NAME="$(
    kubectl get pods \
      --namespace "$INFRA_NAMESPACE" \
      --selector app=mysql \
      --field-selector status.phase=Running \
      --output jsonpath='{.items[0].metadata.name}'
  )"

  [[ -n "$MYSQL_POD_NAME" ]] || {
    echo "Erro: nenhum Pod em execução com o label app=mysql foi encontrado." >&2
    exit 1
  }
}

# Inicia o port-forward do Pod do MySQL em segundo plano e confirma que a
# porta local está disponível antes de continuar.
start_mysql_port_forward() {
  local process_id

  echo "Abrindo localhost:${MYSQL_LOCAL_PORT} para pod/${MYSQL_POD_NAME}:${MYSQL_REMOTE_PORT}..."

  kubectl port-forward \
    --namespace "$INFRA_NAMESPACE" \
    "pod/${MYSQL_POD_NAME}" \
    "${MYSQL_LOCAL_PORT}:${MYSQL_REMOTE_PORT}" \
    >/dev/null 2>&1 &

  process_id=$!
  PORT_FORWARD_PIDS+=("$process_id")
  wait_for_local_port "$MYSQL_LOCAL_PORT" "$process_id" "pod/${MYSQL_POD_NAME}"
}

# Executa o bootstrap original a partir da raiz do user-service, conforme
# exigido pelo próprio script.
run_user_service_bootstrap() {
  (
    cd -- "$USER_SERVICE_DIR"
    "$USER_SERVICE_BOOTSTRAP"
  )
}

# Verifica se o par de chaves JWT foi criado pelo bootstrap original.
validate_jwt_keys() {
  [[ -f "$JWT_PRIVATE_KEY_FILE" ]] || {
    echo "Erro: chave privada JWT não encontrada: ${JWT_PRIVATE_KEY_FILE}" >&2
    exit 1
  }

  [[ -f "$JWT_PUBLIC_KEY_FILE" ]] || {
    echo "Erro: chave pública JWT não encontrada: ${JWT_PUBLIC_KEY_FILE}" >&2
    exit 1
  }
}

# Cria ou atualiza o Secret com nomes de chave iguais aos arquivos esperados
# pelo user-service dentro do container.
create_jwt_secret() {
  kubectl create secret generic "$JWT_SECRET_NAME" \
    --namespace "$SERVICE_NAMESPACE" \
    --from-file="jwt_private_key.pem=${JWT_PRIVATE_KEY_FILE}" \
    --from-file="jwt_public_key.pem=${JWT_PUBLIC_KEY_FILE}" \
    --dry-run=client \
    --output yaml \
    | kubectl apply -f -
}

# Fluxo principal

# Sinais que encerram o script também acionam o trap EXIT, garantindo a
# limpeza sem substituir o comportamento padrão de interrupção do Bash.
trap cleanup_port_forwards EXIT

for command in kubectl python3.11; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "Erro: o comando '${command}' não está instalado ou não está no PATH." >&2
    exit 1
  }
done

[[ -x "$USER_SERVICE_BOOTSTRAP" ]] || {
  echo "Erro: bootstrap não encontrado ou sem permissão de execução: ${USER_SERVICE_BOOTSTRAP}" >&2
  exit 1
}

display_step 'Verificando o Pod do MySQL'

kubectl wait \
  --namespace "$INFRA_NAMESPACE" \
  --for=condition=Ready \
  --timeout=120s \
  pod \
  --selector app=mysql

resolve_mysql_pod_name

display_step 'Iniciando o port-forward do MySQL'
start_mysql_port_forward

display_step 'Executando o bootstrap do user-service'
run_user_service_bootstrap

display_step 'Criando o Secret com as chaves JWT'
validate_jwt_keys
create_jwt_secret

display_step 'Bootstrap do user-service concluído'

exit 0
