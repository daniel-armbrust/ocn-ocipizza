#!/usr/bin/env bash

# Prepara os dados do pizza-service nos Pods de infraestrutura do laboratório.
# Os port-forwards são temporários e encerrados ao finalizar o bootstrap.

set -euo pipefail

# Variáveis globais

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
OKE_FUNDAMENTALS_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
REPOSITORY_DIR="$(cd -- "${OKE_FUNDAMENTALS_DIR}/.." && pwd)"
PIZZA_SERVICE_DIR="${REPOSITORY_DIR}/services/pizza-service"
PIZZA_SERVICE_BOOTSTRAP="${PIZZA_SERVICE_DIR}/bootstrap.sh"

KUBERNETES_NAMESPACE="${KUBERNETES_NAMESPACE:-ocipizza-infra}"
NOSQL_LOCAL_PORT="${NOSQL_LOCAL_PORT:-18080}"
NOSQL_REMOTE_PORT="${NOSQL_REMOTE_PORT:-8080}"
OBJECTSTORAGE_LOCAL_PORT="${OBJECTSTORAGE_LOCAL_PORT:-9000}"
OBJECTSTORAGE_REMOTE_PORT="${OBJECTSTORAGE_REMOTE_PORT:-9000}"
PORT_FORWARD_TIMEOUT_SECONDS="${PORT_FORWARD_TIMEOUT_SECONDS:-30}"

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

# Inicia o port-forward de um Pod em segundo plano e confirma que sua porta
# local está disponível antes de permitir a continuação do bootstrap.
start_port_forward() {
  local pod_name="$1"
  local local_port="$2"
  local remote_port="$3"
  local process_id

  echo "Abrindo localhost:${local_port} para pod/${pod_name}:${remote_port}..."

  kubectl port-forward \
    --namespace "$KUBERNETES_NAMESPACE" \
    "pod/${pod_name}" \
    "${local_port}:${remote_port}" \
    >/dev/null 2>&1 &

  process_id=$!
  PORT_FORWARD_PIDS+=("$process_id")
  wait_for_local_port "$local_port" "$process_id" "pod/${pod_name}"
}

# Executa o bootstrap original do pizza-service com os endpoints locais
# encaminhados para os Pods Oracle NoSQL e MinIO do cluster.
run_pizza_service_bootstrap() {
  APP_ENV=development \
  PERSISTENCE_PROVIDER=nosql \
  NOSQL_PROVIDER=local \
  NOSQL_ENDPOINT="http://127.0.0.1:${NOSQL_LOCAL_PORT}" \
  OBJECTSTORAGE_PROVIDER=local \
  OBJECTSTORAGE_ENDPOINT="http://127.0.0.1:${OBJECTSTORAGE_LOCAL_PORT}" \
  OBJECTSTORAGE_BUCKET="${OBJECTSTORAGE_BUCKET:-pizza-images}" \
  OBJECTSTORAGE_ACCESS_KEY="${OBJECTSTORAGE_ACCESS_KEY:-minioadmin}" \
  OBJECTSTORAGE_SECRET_KEY="${OBJECTSTORAGE_SECRET_KEY:-minioadmin}" \
    "$PIZZA_SERVICE_BOOTSTRAP"
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

[[ -x "$PIZZA_SERVICE_BOOTSTRAP" ]] || {
  echo "Erro: bootstrap não encontrado ou sem permissão de execução: ${PIZZA_SERVICE_BOOTSTRAP}" >&2
  exit 1
}

display_step 'Verificando os Pods de infraestrutura'

# Aguarda os containers antes de iniciar os forwards para evitar conexões
# abertas contra Pods que ainda não estejam prontos.
kubectl wait \
  --namespace "$KUBERNETES_NAMESPACE" \
  --for=condition=Ready \
  --timeout=120s \
  pod/nosql \
  pod/objectstorage

display_step 'Iniciando os port-forwards'

start_port_forward nosql "$NOSQL_LOCAL_PORT" "$NOSQL_REMOTE_PORT"
start_port_forward \
  objectstorage \
  "$OBJECTSTORAGE_LOCAL_PORT" \
  "$OBJECTSTORAGE_REMOTE_PORT"

display_step 'Executando o bootstrap do pizza-service'
run_pizza_service_bootstrap

display_step 'Bootstrap do pizza-service concluído'

exit 0