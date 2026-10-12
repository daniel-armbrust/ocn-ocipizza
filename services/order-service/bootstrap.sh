#!/bin/bash

#
# bootstrap.sh - order-service
#
# Este script prepara o ambiente de desenvolvimento local do order-service.
#
# Etapas executadas:
#
#  1. Valida os requisitos necessários para executar o bootstrap.
#  2. Cria e ativa o ambiente virtual Python.
#  3. Atualiza o pip e instala as dependências do serviço.
#  4. Cria o arquivo .env local, caso ele ainda não exista.
#  5. Carrega as variáveis de ambiente do serviço.
#  6. Cria a tabela de pedidos e seus índices no Oracle NoSQL.
#  7. Finaliza o bootstrap deixando o serviço pronto para execução.
#
# Uso:
#
#     ./bootstrap.sh
#
# O script deve ser executado a partir do diretório raiz do order-service.
#

set -e

display_step() {
    local message="$1"
    local width=64
    local border
    local padding

    printf -v border '%*s' "$width" ''
    border=${border// /#}
    printf -v padding '%*s' "$((width - 4 - ${#message}))" ''

    echo
    echo "$border"
    echo "# $message$padding #"
    echo "$border"
    echo
}

VENV_DIR='.venv'
ENV_FILE='.env'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

display_step 'Iniciando o bootstrap do order-service'

# O requirements.txt identifica a raiz esperada e evita que o bootstrap seja
# executado acidentalmente a partir de outro serviço.
if [ ! -f 'requirements.txt' ]; then
    echo 'Erro: requirements.txt não encontrado.'
    echo 'Execute este script a partir do diretório raiz do order-service.'
    exit 1
fi

if ! command -v python3.11 >/dev/null 2>&1; then
    echo 'Erro: Python 3.11 não foi encontrado.'
    exit 1
fi

display_step 'Preparando o ambiente virtual Python'

if [ ! -d "$VENV_DIR" ]; then
    echo 'Criando ambiente virtual Python...'
    python3.11 -m venv "$VENV_DIR"
else
    echo 'Ambiente virtual Python já existe.'
fi

# As próximas etapas utilizam sempre o interpretador e as dependências
# isoladas do próprio order-service.
source "$VENV_DIR/bin/activate"

display_step 'Atualizando o pip'
python -m pip install --upgrade pip

display_step 'Instalando as dependências Python'
python -m pip install --no-cache-dir -r requirements.txt

display_step 'Configurando o arquivo .env do ambiente local'

if [ ! -f "$ENV_FILE" ]; then
    echo 'Criando arquivo .env para desenvolvimento local...'

    cat > "$ENV_FILE" <<'EOF'
APP_NAME=order-service
APP_ENV=development
DEBUG=true

# Persistência
PERSISTENCE_PROVIDER=nosql

# Oracle NoSQL
NOSQL_TABLE_NAME=orders
NOSQL_ENDPOINT=http://localhost:18080

# JWT
JWT_ISSUER=user-service
JWT_AUDIENCE=oci-pizza
JWT_JWKS_URL=http://localhost:8002/.well-known/jwks.json

# Logging
LOG_LEVEL=INFO
OCI_LOG_ID=
EOF

else
    echo 'Arquivo .env já existe. Nenhuma alteração será realizada.'
fi

# Exporta as configurações para que o módulo Settings e o cliente Oracle
# NoSQL compartilhem exatamente os mesmos valores durante o bootstrap.
echo 'Carregando configurações do ambiente...'

set -a
source "$ENV_FILE"
set +a

display_step 'Inicialização da persistência'

echo "Provider de persistência configurado: ${PERSISTENCE_PROVIDER}"

if [ "${PERSISTENCE_PROVIDER}" != 'nosql' ]; then
    echo "Provider de persistência não suportado pelo bootstrap: ${PERSISTENCE_PROVIDER}"
    exit 1
fi

echo 'Inicializando persistência Oracle NoSQL...'

python <<'PYTHON'
import os
import re

from borneo import TableRequest

from app.repositories.nosql.connection import create_nosql_handle


table_name = os.getenv('NOSQL_TABLE_NAME', 'orders')

# O nome participa diretamente das instruções DDL. A validação impede que um
# valor arbitrário vindo do ambiente altere a estrutura dos comandos.
if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', table_name):
    raise ValueError('NOSQL_TABLE_NAME possui um identificador inválido.')

handle = create_nosql_handle()


def execute_ddl(statement: str, description: str) -> None:
    """
    Executa uma instrução DDL e aguarda sua conclusão no Oracle NoSQL.

    Args:
        statement: Instrução DDL que será submetida ao banco de dados.
        description: Mensagem que identifica a operação em andamento.

    Returns:
        None.

    Raises:
        borneo.NoSQLException: Quando o Oracle NoSQL rejeita a instrução ou
            não consegue concluí-la dentro do período de espera.
    """

    print(description)
    request = TableRequest().set_statement(statement)
    result = handle.table_request(request)
    result.wait_for_completion(handle, 60000, 1000)


drop_statement = f'DROP TABLE IF EXISTS {table_name}'

execute_ddl(
    drop_statement,
    f'Excluindo tabela {table_name}, caso exista...'
)

table_statement = f'''
    CREATE TABLE {table_name} (
        id STRING,
        user_id STRING,
        customer RECORD(
            name STRING,
            email STRING,
            whatsapp STRING
        ),
        delivery_address RECORD(
            zip_code STRING,
            street STRING,
            number STRING,
            complement STRING,
            neighborhood STRING,
            city STRING,
            state STRING
        ),
        items ARRAY(
            RECORD(
                pizza_id STRING,
                name STRING,
                quantity INTEGER,
                unit_price NUMBER,
                subtotal NUMBER
            )
        ),
        subtotal NUMBER,
        delivery_fee NUMBER,
        total NUMBER,
        status STRING,
        payment_status STRING,
        idempotency_key STRING,
        created_at TIMESTAMP(3),
        updated_at TIMESTAMP(3),
        PRIMARY KEY(SHARD(user_id), id)
    )
'''

index_statements = (
    (
        f'CREATE INDEX idx_orders_id ON {table_name}(id)',
        'Criando índice para consulta administrativa por pedido...'
    ),
    (
        f'CREATE INDEX idx_orders_user_created_at '
        f'ON {table_name}(user_id, created_at)',
        'Criando índice para ordenar os pedidos de um usuário...'
    ),
    (
        f'CREATE INDEX idx_orders_user_idempotency '
        f'ON {table_name}(user_id, idempotency_key)',
        'Criando índice para consulta por idempotência...'
    ),
    (
        f'CREATE INDEX idx_orders_status '
        f'ON {table_name}(status)',
        'Criando índice para consulta dos pedidos por status...'
    ),
    (
        f'CREATE INDEX idx_orders_created_at '
        f'ON {table_name}(created_at)',
        'Criando índice para ordenar todos os pedidos...'
    ),
    (
        f'CREATE INDEX idx_orders_status_created_at '
        f'ON {table_name}(status, created_at)',
        'Criando índice para ordenar os pedidos por status...'
    ),
    (
        f'CREATE INDEX idx_orders_payment_created_at '
        f'ON {table_name}(payment_status, created_at)',
        'Criando índice para ordenar os pedidos por pagamento...'
    ),
    (
        f'CREATE INDEX idx_orders_status_payment_created_at '
        f'ON {table_name}(status, payment_status, created_at)',
        'Criando índice para ordenar os pedidos pelos dois status...'
    )
)

try:
    execute_ddl(
        table_statement,
        f'Criando tabela {table_name}...'
    )

    for statement, description in index_statements:
        execute_ddl(statement, description)
finally:
    handle.close()

print(f'Tabela {table_name} e índices prontos para utilização.')
PYTHON

display_step 'Bootstrap do order-service concluído com sucesso'

exit 0
