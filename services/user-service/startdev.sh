#!/bin/bash

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Variáveis exportadas pelo ambiente externo têm precedência sobre o .env.
declare -A ENVIRONMENT_OVERRIDES

for variable in \
    APP_NAME APP_ENV DEBUG LOG_LEVEL OCI_LOG_ID \
    PERSISTENCE_PROVIDER DATABASE_URL \
    MESSAGING_PROVIDER QUEUE_NAME RABBITMQ_HOST RABBITMQ_PORT \
    RABBITMQ_USERNAME RABBITMQ_PASSWORD OCI_QUEUE_ID \
    OCI_REGION OCI_AUTH_MODE OCI_CONFIG_FILE OCI_CONFIG_PROFILE \
    JWT_KEY_PROVIDER JWT_ISSUER JWT_AUDIENCE \
    JWT_ACCESS_TOKEN_EXPIRATION_MINUTES JWT_PRIVATE_KEY_PATH \
    JWT_PUBLIC_KEY_PATH JWT_PRIVATE_KEY_SECRET_ID \
    REFRESH_TOKEN_EXPIRATION_DAYS; do
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
export APP_NAME="${APP_NAME:-user-service}"
export APP_ENV="${APP_ENV:-development}"
export DEBUG="${DEBUG:-true}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"
export OCI_LOG_ID="${OCI_LOG_ID:-}"

export PERSISTENCE_PROVIDER="${PERSISTENCE_PROVIDER:-sqlalchemy}"
export DATABASE_URL="${DATABASE_URL:-mysql+pymysql://user_service:user_service@127.0.0.1:13306/users}"

export MESSAGING_PROVIDER="${MESSAGING_PROVIDER:-rabbitmq}"
export QUEUE_NAME="${QUEUE_NAME:-notifications-queue}"
export RABBITMQ_HOST="${RABBITMQ_HOST:-127.0.0.1}"
export RABBITMQ_PORT="${RABBITMQ_PORT:-5672}"
export RABBITMQ_USERNAME="${RABBITMQ_USERNAME:-oci_pizza}"
export RABBITMQ_PASSWORD="${RABBITMQ_PASSWORD:-oci_pizza}"
export OCI_QUEUE_ID="${OCI_QUEUE_ID:-}"

export OCI_REGION="${OCI_REGION:-sa-saopaulo-1}"
export OCI_AUTH_MODE="${OCI_AUTH_MODE:-}"
export OCI_CONFIG_FILE="${OCI_CONFIG_FILE:-${HOME}/.oci/config}"
export OCI_CONFIG_PROFILE="${OCI_CONFIG_PROFILE:-DEFAULT}"

export JWT_KEY_PROVIDER="${JWT_KEY_PROVIDER:-local}"
export JWT_ISSUER="${JWT_ISSUER:-user-service}"
export JWT_AUDIENCE="${JWT_AUDIENCE:-ocipizza}"
export JWT_ACCESS_TOKEN_EXPIRATION_MINUTES="${JWT_ACCESS_TOKEN_EXPIRATION_MINUTES:-15}"
export JWT_PRIVATE_KEY_PATH="${JWT_PRIVATE_KEY_PATH:-secrets/jwt_private_key.pem}"
export JWT_PUBLIC_KEY_PATH="${JWT_PUBLIC_KEY_PATH:-secrets/jwt_public_key.pem}"
export JWT_PRIVATE_KEY_SECRET_ID="${JWT_PRIVATE_KEY_SECRET_ID:-}"
export REFRESH_TOKEN_EXPIRATION_DAYS="${REFRESH_TOKEN_EXPIRATION_DAYS:-30}"

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


# ----------------------------------
# Aplicação
# ----------------------------------

echo "Iniciando user-service em modo de desenvolvimento..."

uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8002 \
    --reload
