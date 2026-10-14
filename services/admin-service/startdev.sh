#!/bin/bash

set -e

# Variáveis utilizadas pelo admin-service em desenvolvimento.
export APP_ENV="development"
export LOG_LEVEL="INFO"

# Serviço REDIS
export REDIS_ENDPOINT="redis://redis:16379/1"

# Chaves utilizadas pelas sessões internas e pela proteção CSRF
# mantidas pelo frontend-service.
export SESSION_SECRET_KEY="!!!Sup3rS3cr3t0!!!"
export CSRF_SECRET_KEY="!!!Sup3rS3cr3t0!!!"

# URLs dos microserviços acessíveis a partir da máquina local.
export PIZZA_SERVICE_URL="http://localhost:8001"
export USER_SERVICE_URL="http://localhost:8002"
export DELIVERY_SERVICE_URL="http://localhost:8003"
export ORDER_SERVICE_URL="http://localhost:8004"
export NOTIFICATION_SERVICE_URL="http://localhost:8005"

# JWT
export JWT_ISSUER="user-service"
export JWT_AUDIENCE="ocipizza"
export JWT_JWKS_URL="http://localhost:8002/.well-known/jwks.json"

# Object Storage
export OBJECTSTORAGE_ENDPOINT="http://localhost:9000"
export OBJECTSTORAGE_ACCESS_KEY="minioadmin"
export OBJECTSTORAGE_SECRET_KEY="minioadmin"
export PIZZA_IMAGES_OBJECTSTORAGE_BUCKET="pizza-images"

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

echo "Iniciando admin-service em modo de desenvolvimento..."

uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8006 \
    --reload
