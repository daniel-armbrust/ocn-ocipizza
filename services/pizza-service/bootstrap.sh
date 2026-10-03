#!/bin/bash

#
# bootstrap.sh - pizza-service
#
# Este script prepara o ambiente de desenvolvimento local do pizza-service.
#
# Etapas executadas:
#
#  1. Cria o ambiente virtual Python, caso ainda não exista.
#  2. Ativa o ambiente virtual.
#  3. Atualiza o pip.
#  4. Instala as dependências definidas em requirements.txt.
#  5. Cria o arquivo .env local, caso ainda não exista.
#  6. Carrega as variáveis definidas no arquivo .env.
#  7. Identifica o provider de persistência configurado.
#  8. Inicializa a persistência necessária para o provider selecionado.
#  9. Cria a tabela de pizzas no Oracle NoSQL, quando necessário.
# 10. Finaliza o bootstrap deixando o serviço pronto para execução.
#
# Uso:
#
#     ./bootstrap.sh
#
# O script deve ser executado a partir do diretório raiz do pizza-service.
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

# Configurações utilizadas pelo ambiente local de desenvolvimento.

VENV_DIR='.venv'
ENV_FILE='.env'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

display_step 'Iniciando o bootstrap do pizza-service'

# Verifica se o script está sendo executado na raiz do pizza-service.

if [ ! -f 'requirements.txt' ]; then
    echo 'Erro: requirements.txt não encontrado.'
    echo 'Execute este script a partir do diretório raiz do pizza-service.'
    exit 1
fi

# Verifica se o Python 3.11 está disponível.

if ! command -v python3.11 >/dev/null 2>&1; then
    echo 'Erro: Python 3.11 não foi encontrado.'
    exit 1
fi

display_step 'Preparando o ambiente virtual Python'

if [ ! -d ".venv" ]; then
    echo 'Criando ambiente virtual Python...'
    python3.11 -m venv .venv
else
    echo 'Ambiente virtual Python já existe.'
fi

# Ativa o ambiente virtual Python.
source "$VENV_DIR/bin/activate"

display_step 'Atualizando o pip'
python -m pip install --upgrade pip

display_step 'Instalando as dependências Python'
python -m pip install --no-cache-dir -r requirements.txt

display_step 'Configurando o arquivo .env do ambiente local'

if [ ! -f "$ENV_FILE" ]; then
    echo 'Criando arquivo .env para desenvolvimento local...'

    cat > .env <<'EOF'
APP_NAME=pizza-service
APP_ENV=development
DEBUG=true

# Persistência
PERSISTENCE_PROVIDER=nosql

# Oracle NoSQL
NOSQL_TABLE_NAME=pizzas
NOSQL_ENDPOINT=http://localhost:18080

# JWT
JWT_ISSUER=user-service
JWT_AUDIENCE=oci-pizza
JWT_JWKS_URL=http://localhost:8002/.well-known/jwks.json
EOF

else
    echo 'Arquivo .env já existe.'
fi

# Carregamento das variáveis do .env

echo "Carregando configurações do ambiente..."

set -a
source .env
set +a

# Persistência

display_step 'Inicialização da persistência'

echo "Provider de persistência configurado: ${PERSISTENCE_PROVIDER}"

if [ "${PERSISTENCE_PROVIDER}" = "nosql" ]; then
    echo 'Inicializando persistência Oracle NoSQL...'

    python <<'PYTHON'
import os

from borneo import NoSQLHandleConfig, TableRequest

from app.repositories.nosql.connection import get_nosql_handle

table_name = os.getenv(
    'NOSQL_TABLE_NAME',
    'pizzas'
)

handle = get_nosql_handle()

statement = f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        id STRING,
        name STRING,
        description STRING,
        category STRING,
        price NUMBER,
        image_name STRING,
        available BOOLEAN,
        created_at TIMESTAMP(3),
        updated_at TIMESTAMP(3),
        PRIMARY KEY(id)
    )
'''

print(f'Criando tabela {table_name}, caso ainda não exista...')

request = TableRequest().set_statement(statement)
result = handle.table_request(request)
result.wait_for_completion(handle, 60000, 1000)

print(f'Tabela {table_name} pronta para utilização.')

handle.close()
PYTHON

elif [ "${PERSISTENCE_PROVIDER}" = "sqlalchemy" ]; then
    echo 'Inicializando persistência SQLAlchemy...'

    if [ ! -f 'alembic.ini' ] || [ ! -f 'alembic/env.py' ]; then
        echo 'Estrutura do Alembic não encontrada.'
        echo 'Inicializando o Alembic...'

        rm -rf alembic
        rm -f alembic.ini

        alembic init alembic

        echo 'Configurando o ambiente do Alembic...'

        cat > alembic/env.py <<'PYTHON'
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.config.settings import settings

from app.repositories.orm.base import Base

#
# Os imports abaixo registram os modelos ORM no Base.metadata.
#
# O Alembic utiliza esses metadados durante o processo de autogenerate
# para comparar os modelos definidos pela aplicação com o schema atual
# existente no banco de dados.
#

from app.repositories.orm.pizza_orm import PizzaORM

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

#
# Substitui a URL configurada no alembic.ini pela DATABASE_URL
# utilizada pela própria aplicação.
#

config.set_main_option(
    'sqlalchemy.url',
    settings.database_url
)

#
# Metadados utilizados pelo Alembic para detectar alterações
# nas tabelas durante o processo de autogenerate.
#
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """
    Executa migrations sem estabelecer uma conexão direta com o banco.
    """

    url = config.get_main_option('sqlalchemy.url')

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            'paramstyle': 'named'
        },
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """
    Executa migrations utilizando uma conexão com o banco de dados.
    """

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {}
        ),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
PYTHON

    else
        echo 'Estrutura do Alembic já existe.'
    fi

    display_step 'Verificando as migrations do Alembic'

    if ! find alembic/versions -maxdepth 1 -type f -name '*.py' | grep -q .; then
        echo 'Nenhuma migration encontrada.'
        echo 'Gerando migration inicial do user-service...'

        alembic revision \
            --autogenerate \
            -m 'create initial user service tables'

    else
        echo 'Migrations do Alembic já existem.'
    fi

    display_step 'Aplicando as migrations do banco de dados'

    alembic upgrade head

    display_step 'Criando os usuários do ambiente de demonstração'
    # TODO

else
    echo "Provider de persistência não suportado: ${PERSISTENCE_PROVIDER}"
    exit 1
fi

# Dados de demonstração
if [ "${APP_ENV}" = "development" ]; then
    display_step 'Criando pizzas de demonstração...'

    python <<'PYTHON'
from app.dependencies.database import get_pizza_repository
from seeds.pizza_seed import get_demo_pizzas

repository = get_pizza_repository()

for pizza in get_demo_pizzas():
    existing_pizza = repository.get_by_id(pizza.id)

    if existing_pizza is not None:
        print(f'Pizza de demonstração já existe: {pizza.name}')
        continue

    repository.create(pizza)

    print(f'Pizza de demonstração criada: {pizza.name}')
PYTHON
fi

display_step 'Bootstrap do pizza-service concluído com sucesso'

exit 0