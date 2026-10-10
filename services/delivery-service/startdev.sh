#!/bin/bash

set -e

# Variáveis utilizadas pelo user-service em desenvolvimento.
export APP_ENV="development"
export LOG_LEVEL="INFO"

export PERSISTENCE_PROVIDER="nosql"

export NOSQL_TABLE_NAME="delivery_areas"
export NOSQL_ENDPOINT="http://localhost:18080"

export JWT_ISSUER="user-service"
export JWT_AUDIENCE="oci-pizza"
export JWT_JWKS_URL="http://localhost:8002/.well-known/jwks.json"

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

echo "Iniciando delivery-service em modo de desenvolvimento..."

uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8003 \
    --reload
