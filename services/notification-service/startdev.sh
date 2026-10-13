#!/bin/bash

set -e

# Variáveis utilizadas pelo notification-service em desenvolvimento.
export APP_ENV="development"
export LOG_LEVEL="INFO"

export SITE_URL="http://localhost:8010"

export EMAIL_PROVIDER="smtp"
export SMTP_HOST="localhost"
export SMTP_PORT="1025"
export SMTP_USERNAME=""
export SMTP_PASSWORD=""
export SMTP_USE_TLS="false"

export MESSAGING_PROVIDER="rabbitmq"
export RABBITMQ_HOST="localhost"
export RABBITMQ_PORT="5672"
export RABBITMQ_USERNAME="oci_pizza"
export RABBITMQ_PASSWORD="oci_pizza"
export QUEUE_NAME="notifications-queue"

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

echo "Iniciando notification-service em modo de desenvolvimento..."

uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8005 \
    --reload
