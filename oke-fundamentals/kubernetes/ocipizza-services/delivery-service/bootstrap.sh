#!/usr/bin/env bash

# Prepara os dados do delivery-service utilizando o Pod de Oracle NoSQL
# executado na infraestrutura do laboratório.
# O port-forward é temporário e encerrado ao finalizar o bootstrap.

set -euo pipefail

# Variáveis globais

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# A estrutura posiciona este script três níveis abaixo de oke-fundamentals:
# kubernetes/ocipizza-services/delivery-service/.
OKE_FUNDAMENTALS_DIR="$(cd -- "${SCRIPT_DIR}/../../.." && pwd)"
REPOSITORY_DIR="$(cd -- "${OKE_FUNDAMENTALS_DIR}/.." && pwd)"
DELIVERY_SERVICE_DIR="${REPOSITORY_DIR}/services/delivery-service"
DELIVERY_SERVICE_BOOTSTRAP="${DELIVERY_SERVICE_DIR}/bootstrap.sh"

KUBERNETES_NAMESPACE="${KUBERNETES_NAMESPACE:-ocipizza-infra}"
NOSQL_LOCAL_PORT="${NOSQL_LOCAL_PORT:-18080}"
NOSQL_REMOTE_PORT="${NOSQL_REMOTE_PORT:-8080}"
PORT_FORWARD_TIMEOUT_SECONDS="${PORT_FORWARD_TIMEOUT_SECONDS:-30}"

NOSQL_POD_NAME=""
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

# Aguarda o Pod de NoSQL ficar pronto e retorna seu nome atual a partir do
# label app. Os controladores geram nomes dinâmicos para os Pods.
resolve_nosql_pod_name() {
  kubectl wait \
    --namespace "$KUBERNETES_NAMESPACE" \
    --for=condition=Ready \
    --timeout=120s \
    --selector app=nosql \
    pod \
    >/dev/null

  NOSQL_POD_NAME="$(
    kubectl get pods \
      --namespace "$KUBERNETES_NAMESPACE" \
      --selector app=nosql \
      --field-selector status.phase=Running \
      --output jsonpath='{.items[0].metadata.name}'
  )"

  [[ -n "$NOSQL_POD_NAME" ]] || {
    echo 'Erro: nenhum Pod em execução com o label app=nosql foi encontrado.' >&2
    exit 1
  }
}

# Inicia o port-forward do Pod de NoSQL e confirma que a porta local está
# disponível antes de permitir a continuação do bootstrap.
start_nosql_port_forward() {
  local process_id

  echo "Abrindo localhost:${NOSQL_LOCAL_PORT} para pod/${NOSQL_POD_NAME}:${NOSQL_REMOTE_PORT}..."

  kubectl port-forward \
    --namespace "$KUBERNETES_NAMESPACE" \
    "pod/${NOSQL_POD_NAME}" \
    "${NOSQL_LOCAL_PORT}:${NOSQL_REMOTE_PORT}" \
    >/dev/null 2>&1 &

  process_id=$!
  PORT_FORWARD_PIDS+=("$process_id")
  wait_for_local_port "$NOSQL_LOCAL_PORT" "$process_id" "pod/${NOSQL_POD_NAME}"
}

# Executa o bootstrap original do delivery-service com o endpoint local do
# NoSQL encaminhado para o Pod do cluster.
run_delivery_service_bootstrap() {
  (
    cd -- "$DELIVERY_SERVICE_DIR"
    NOSQL_PROVIDER=local \
    NOSQL_ENDPOINT="http://127.0.0.1:${NOSQL_LOCAL_PORT}" \
      "$DELIVERY_SERVICE_BOOTSTRAP"
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

[[ -x "$DELIVERY_SERVICE_BOOTSTRAP" ]] || {
  echo "Erro: bootstrap não encontrado ou sem permissão de execução: ${DELIVERY_SERVICE_BOOTSTRAP}" >&2
  exit 1
}

display_step 'Verificando o Pod de infraestrutura'
resolve_nosql_pod_name

display_step 'Iniciando o port-forward do NoSQL'
start_nosql_port_forward

display_step 'Executando o bootstrap do delivery-service'
run_delivery_service_bootstrap

display_step 'Bootstrap do delivery-service concluído'

exit 0
