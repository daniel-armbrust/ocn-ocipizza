#!/bin/bash

set -e

# Variáveis exportadas pelo ambiente externo têm precedência sobre o .env.
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

declare -A ENVIRONMENT_OVERRIDES

for variable in \
    APP_ENV LOG_LEVEL SITE_URL EMAIL_TEMPLATES_PATH \
    MESSAGING_PROVIDER QUEUE_NAME OCI_QUEUE_ID QUEUE_COMPARTMENT_ID \
    RABBITMQ_HOST RABBITMQ_PORT RABBITMQ_USERNAME RABBITMQ_PASSWORD \
    EMAIL_PROVIDER SMTP_HOST SMTP_PORT SMTP_USERNAME SMTP_PASSWORD \
    SMTP_USE_TLS SMTP_EMAIL_SENDER OCI_EMAIL_DELIVERY_COMPARTMENT_ID \
    OCI_EMAIL_SENDER_NAME OCI_REGION OCI_AUTH_MODE OCI_CONFIG_FILE \
    OCI_CONFIG_PROFILE NOTIFICATION_POLL_INTERVAL \
    NOTIFICATION_RETRY_INTERVAL; do
    if [[ -v "$variable" ]]; then
        ENVIRONMENT_OVERRIDES["$variable"]="${!variable}"
    fi
done

if [ -f '.env' ]; then
    set -a
    source .env
    set +a
fi

for variable in "${!ENVIRONMENT_OVERRIDES[@]}"; do
    export "$variable=${ENVIRONMENT_OVERRIDES[$variable]}"
done

# Valores padrão utilizados quando não foram definidos no ambiente ou no .env.
export APP_ENV="${APP_ENV:-development}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"

export SITE_URL="${SITE_URL:-http://localhost:8010}"
export EMAIL_TEMPLATES_PATH="${EMAIL_TEMPLATES_PATH:-app/templates/emails}"

export EMAIL_PROVIDER="${EMAIL_PROVIDER:-smtp}"
export SMTP_HOST="${SMTP_HOST:-localhost}"
export SMTP_PORT="${SMTP_PORT:-1025}"
export SMTP_USERNAME="${SMTP_USERNAME:-}"
export SMTP_PASSWORD="${SMTP_PASSWORD:-}"
export SMTP_USE_TLS="${SMTP_USE_TLS:-false}"
export SMTP_EMAIL_SENDER="${SMTP_EMAIL_SENDER:-no-reply@ocipizza.local}"
export OCI_EMAIL_DELIVERY_COMPARTMENT_ID="${OCI_EMAIL_DELIVERY_COMPARTMENT_ID:-}"
export OCI_EMAIL_SENDER_NAME="${OCI_EMAIL_SENDER_NAME:-OCI Pizza}"

export MESSAGING_PROVIDER="${MESSAGING_PROVIDER:-rabbitmq}"
export RABBITMQ_HOST="${RABBITMQ_HOST:-localhost}"
export RABBITMQ_PORT="${RABBITMQ_PORT:-5672}"
export RABBITMQ_USERNAME="${RABBITMQ_USERNAME:-oci_pizza}"
export RABBITMQ_PASSWORD="${RABBITMQ_PASSWORD:-oci_pizza}"
export QUEUE_NAME="${QUEUE_NAME:-notifications-queue}"
export OCI_QUEUE_ID="${OCI_QUEUE_ID:-}"
export QUEUE_COMPARTMENT_ID="${QUEUE_COMPARTMENT_ID:-}"

export OCI_REGION="${OCI_REGION:-sa-saopaulo-1}"
export OCI_AUTH_MODE="${OCI_AUTH_MODE:-config_file}"
export OCI_CONFIG_FILE="${OCI_CONFIG_FILE:-${HOME}/.oci/config}"
export OCI_CONFIG_PROFILE="${OCI_CONFIG_PROFILE:-DEFAULT}"

export NOTIFICATION_POLL_INTERVAL="${NOTIFICATION_POLL_INTERVAL:-5.0}"
export NOTIFICATION_RETRY_INTERVAL="${NOTIFICATION_RETRY_INTERVAL:-10.0}"

# ----------------------------------
# Ambiente virtual
# ----------------------------------

if [ ! -d ".venv" ]; then
    echo "Criando ambiente virtual..."
    python3.11 -m venv .venv
fi

echo "Ativando ambiente virtual..."
source .venv/bin/activate


# ----------------------------------
# Dependências
# ----------------------------------

echo "Instalando dependências..."
pip install -r requirements.txt

if [ "${OCI_AUTH_MODE}" = 'config_file' ] && \
   { [ "${MESSAGING_PROVIDER}" = 'oci_queue' ] || \
     [ "${EMAIL_PROVIDER}" = 'oci' ]; } && \
   [ ! -f "${OCI_CONFIG_FILE}" ]; then
    echo "Erro: arquivo de configuração OCI não encontrado: ${OCI_CONFIG_FILE}"
    exit 1
fi

if [ "${MESSAGING_PROVIDER}" = 'oci_queue' ] && \
   [ -z "${OCI_QUEUE_ID}" ]; then
    echo "Localizando a fila OCI Queue..."

    if [ "${OCI_AUTH_MODE}" = 'config_file' ] && \
       [ ! -f "${OCI_CONFIG_FILE}" ]; then
        echo "Erro: arquivo de configuração OCI não encontrado: ${OCI_CONFIG_FILE}"
        exit 1
    fi

    if [ -z "${QUEUE_COMPARTMENT_ID}" ]; then
        echo 'Erro: QUEUE_COMPARTMENT_ID é obrigatório para OCI Queue.'
        exit 1
    fi

    OCI_QUEUE_ID="$(python - <<'PYTHON'
import os

import oci
import oci.queue

from oci.auth.signers import InstancePrincipalsSecurityTokenSigner


if os.environ['OCI_AUTH_MODE'] == 'config_file':
    config = oci.config.from_file(
        file_location=os.environ['OCI_CONFIG_FILE'],
        profile_name=os.environ.get('OCI_CONFIG_PROFILE')
    )
    config['region'] = os.environ['OCI_REGION']
    queue_admin_client = oci.queue.QueueAdminClient(config=config)
else:
    signer = InstancePrincipalsSecurityTokenSigner()
    queue_admin_client = oci.queue.QueueAdminClient(
        config={'region': signer.region},
        signer=signer
    )


queue_collection = queue_admin_client.list_queues(
    compartment_id=os.environ['QUEUE_COMPARTMENT_ID'],
    display_name=os.environ['QUEUE_NAME']
).data

if not queue_collection.items:
    raise RuntimeError(
        'A fila OCI Queue não foi encontrada. Execute bootstrap.sh antes '
        'de iniciar o serviço.'
    )

print(queue_collection.items[0].id)
PYTHON
)"
    export OCI_QUEUE_ID
    echo "Fila OCI Queue encontrada: ${OCI_QUEUE_ID}"
fi


# ----------------------------------
# Aplicação
# ----------------------------------

echo "Iniciando notification-service em modo de desenvolvimento..."

uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8005 \
    --reload
