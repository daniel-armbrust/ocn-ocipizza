#!/bin/bash

set -e

# Variáveis utilizadas pelo frontend-service em desenvolvimento.
export APP_ENV=development
export LOG_LEVEL=INFO
export HTTP_CLIENT_TIMEOUT=10

# URLs dos microserviços acessíveis a partir da máquina local.
export PIZZA_SERVICE_URL=http://pizza-service:8001
export USER_SERVICE_URL=http://user-service:8002

# Serviço REDIS
export REDIS_ENDPOINT=redis://redis:6379/0

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

echo "Iniciando frontend-service em modo de desenvolvimento..."

uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8010 \
    --reload