#!/bin/bash

set -e

# Este script somente inicia o serviço em modo de desenvolvimento.
# A preparação do ambiente e a carga dos dados são responsabilidades do
# bootstrap.sh.

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Variáveis exportadas pelo ambiente externo têm precedência sobre o .env.
declare -A ENVIRONMENT_OVERRIDES

for variable in \
    APP_ENV LOG_LEVEL PERSISTENCE_PROVIDER NOSQL_PROVIDER NOSQL_TABLE_NAME \
    NOSQL_ENDPOINT NOSQL_COMPARTMENT_ID OCI_REGION OCI_AUTH_MODE \
    OCI_CONFIG_FILE OCI_CONFIG_PROFILE JWT_ISSUER JWT_AUDIENCE JWT_JWKS_URL; do
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

export PERSISTENCE_PROVIDER="${PERSISTENCE_PROVIDER:-nosql}"

export NOSQL_PROVIDER="${NOSQL_PROVIDER:-local}"
export NOSQL_TABLE_NAME="${NOSQL_TABLE_NAME:-delivery_areas}"
export NOSQL_ENDPOINT="${NOSQL_ENDPOINT:-http://localhost:18080}"
export NOSQL_COMPARTMENT_ID="${NOSQL_COMPARTMENT_ID:-}"

export OCI_REGION="${OCI_REGION:-sa-saopaulo-1}"
export OCI_AUTH_MODE="${OCI_AUTH_MODE:-config_file}"
export OCI_CONFIG_FILE="${OCI_CONFIG_FILE:-${HOME}/.oci/config}"
export OCI_CONFIG_PROFILE="${OCI_CONFIG_PROFILE:-DEFAULT}"

export JWT_ISSUER="${JWT_ISSUER:-user-service}"
export JWT_AUDIENCE="${JWT_AUDIENCE:-ocipizza}"
export JWT_JWKS_URL="${JWT_JWKS_URL:-http://localhost:8002/.well-known/jwks.json}"

# Valida as configurações antes de iniciar a aplicação para evitar falhas
# tardias durante a criação do cliente de persistência.
if [ "${PERSISTENCE_PROVIDER}" != 'nosql' ] && \
   [ "${PERSISTENCE_PROVIDER}" != 'sqlalchemy' ]; then
    echo "Provider de persistência não suportado: ${PERSISTENCE_PROVIDER}"
    exit 1
fi

if [ "${NOSQL_PROVIDER}" != 'local' ] && \
   [ "${NOSQL_PROVIDER}" != 'oci' ]; then
    echo "Provider NoSQL não suportado: ${NOSQL_PROVIDER}"
    echo 'Utilize NOSQL_PROVIDER=local ou NOSQL_PROVIDER=oci.'
    exit 1
fi

if [ "${PERSISTENCE_PROVIDER}" = 'nosql' ] && \
   [ "${NOSQL_PROVIDER}" != 'local' ] && \
   [ -z "${NOSQL_COMPARTMENT_ID}" ]; then
    echo 'Erro: NOSQL_COMPARTMENT_ID é obrigatório quando '
    echo 'NOSQL_PROVIDER for diferente de local.'
    exit 1
fi

if [ "${NOSQL_PROVIDER}" = 'oci' ]; then
    if [ "${OCI_AUTH_MODE}" != 'config_file' ] && \
       [ "${OCI_AUTH_MODE}" != 'instance_principal' ]; then
        echo "Modo de autenticação OCI não suportado: ${OCI_AUTH_MODE}"
        echo "Utilize OCI_AUTH_MODE=config_file ou "\
            "OCI_AUTH_MODE=instance_principal."
        exit 1
    fi
fi

if [ "${NOSQL_PROVIDER}" = 'oci' ] && \
   [ "${OCI_AUTH_MODE}" = 'config_file' ] && \
   [ ! -f "${OCI_CONFIG_FILE}" ]; then
    echo "Erro: arquivo de configuração OCI não encontrado: ${OCI_CONFIG_FILE}"
    exit 1
fi

# O ambiente virtual e as dependências são preparados pelo bootstrap.sh.
if [ ! -x '.venv/bin/python' ]; then
    echo 'Erro: ambiente virtual não encontrado.'
    echo 'Execute ./bootstrap.sh antes de iniciar o serviço.'
    exit 1
fi

echo 'Ativando ambiente virtual...'
source .venv/bin/activate

echo 'Iniciando delivery-service em modo de desenvolvimento...'

python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8003 \
    --reload
