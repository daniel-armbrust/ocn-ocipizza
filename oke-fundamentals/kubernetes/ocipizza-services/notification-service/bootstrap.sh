#!/usr/bin/env bash

# Prepara o notification-service utilizando o RabbitMQ executado na
# infraestrutura do laboratório. O Mailpit é utilizado pelo serviço em
# execução, mas não é necessário durante este bootstrap.

set -euo pipefail

# Variáveis globais

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# A estrutura posiciona este script três níveis abaixo de oke-fundamentals:
# kubernetes/ocipizza-services/notification-service/.
OKE_FUNDAMENTALS_DIR="$(cd -- "${SCRIPT_DIR}/../../.." && pwd)"
REPOSITORY_DIR="$(cd -- "${OKE_FUNDAMENTALS_DIR}/.." && pwd)"
NOTIFICATION_SERVICE_DIR="${REPOSITORY_DIR}/services/notification-service"
NOTIFICATION_SERVICE_BOOTSTRAP="${NOTIFICATION_SERVICE_DIR}/bootstrap.sh"

KUBERNETES_NAMESPACE="${KUBERNETES_NAMESPACE:-ocipizza-infra}"
RABBITMQ_LOCAL_PORT="${RABBITMQ_LOCAL_PORT:-5672}"
RABBITMQ_REMOTE_PORT="${RABBITMQ_REMOTE_PORT:-5672}"
PORT_FORWARD_TIMEOUT_SECONDS="${PORT_FORWARD_TIMEOUT_SECONDS:-30}"

RABBITMQ_POD_NAME=""
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

# Aguarda um Pod ficar pronto e retorna seu nome atual a partir do label app.
# Os controladores geram nomes dinâmicos para os Pods.
resolve_ready_pod_name() {
  local app_label="$1"
  local pod_name

  kubectl wait \
    --namespace "$KUBERNETES_NAMESPACE" \
    --for=condition=Ready \
    --timeout=120s \
    --selector "app=${app_label}" \
    pod \
    >/dev/null

  pod_name="$(
    kubectl get pods \
      --namespace "$KUBERNETES_NAMESPACE" \
      --selector "app=${app_label}" \
      --field-selector status.phase=Running \
      --output jsonpath='{.items[0].metadata.name}'
  )"

  [[ -n "$pod_name" ]] || {
    echo "Erro: nenhum Pod em execução foi encontrado para app=${app_label}." >&2
    return 1
  }

  printf '%s\n' "$pod_name"
}

# Inicia um port-forward de um Pod e confirma que sua porta local está
# disponível antes de permitir a continuação do bootstrap.
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

# Executa o bootstrap original com o endpoint local encaminhado para o Pod
# de RabbitMQ. O Mailpit é utilizado pelo serviço em execução.
run_notification_service_bootstrap() {
  (
    cd -- "$NOTIFICATION_SERVICE_DIR"
    MESSAGING_PROVIDER=rabbitmq \
    RABBITMQ_HOST=127.0.0.1 \
    RABBITMQ_PORT="$RABBITMQ_LOCAL_PORT" \
      "$NOTIFICATION_SERVICE_BOOTSTRAP"
  )
}

# Fluxo principal

trap cleanup_port_forwards EXIT

for command in kubectl python3.11; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "Erro: o comando '${command}' não está instalado ou não está no PATH." >&2
    exit 1
  }
done

[[ -x "$NOTIFICATION_SERVICE_BOOTSTRAP" ]] || {
  echo "Erro: bootstrap não encontrado ou sem permissão de execução: ${NOTIFICATION_SERVICE_BOOTSTRAP}" >&2
  exit 1
}

display_step 'Verificando os Pods de infraestrutura'

RABBITMQ_POD_NAME="$(resolve_ready_pod_name rabbitmq)"

display_step 'Iniciando os port-forwards'

start_port_forward "$RABBITMQ_POD_NAME" "$RABBITMQ_LOCAL_PORT" "$RABBITMQ_REMOTE_PORT"

display_step 'Executando o bootstrap do notification-service'
run_notification_service_bootstrap

display_step 'Bootstrap do notification-service concluído'

exit 0
