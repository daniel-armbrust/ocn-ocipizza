#!/bin/bash

set -e

# Variáveis utilizadas pelo user-service em desenvolvimento.
export APP_ENV="development"
export LOG_LEVEL="INFO"

export DATABASE_URL="mysql+pymysql://user_service:user_service@localhost:13306/users"

export MESSAGING_PROVIDER="rabbitmq"
export RABBITMQ_HOST="localhost"
export RABBITMQ_PORT="5672"
export RABBITMQ_PASSWORD="oci_pizza"
export RABBITMQ_QUEUE_NAME="notifications"

export JWT_KEY_PROVIDER="local"
export JWT_ISSUER="user-service"
export JWT_AUDIENCE="oci-pizza"
export JWT_ACCESS_TOKEN_EXPIRATION_MINUTES="15"
export JWT_PRIVATE_KEY_PATH="./secrets/jwt_private_key.pem"
export JWT_PUBLIC_KEY_PATH="./secrets/jwt_public_key.pem"

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
