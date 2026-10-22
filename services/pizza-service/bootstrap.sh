#!/bin/bash

#
# bootstrap.sh - pizza-service
#
# Este script prepara o ambiente configurado do pizza-service.
#
# Etapas executadas:
#
#  1. Cria o ambiente virtual Python, caso ainda não exista.
#  2. Ativa o ambiente virtual.
#  3. Atualiza o pip.
#  4. Instala as dependências definidas em requirements.txt.
#  5. Cria o arquivo .env local, caso ainda não exista.
#  6. Carrega as variáveis definidas no arquivo .env.
#  7. Identifica os providers de persistência e Object Storage configurados.
#  8. Valida os providers e as configurações obrigatórias do ambiente.
#  9. Inicializa a persistência necessária para o provider selecionado.
# 10. Cria a tabela no backend NoSQL ou aplica as migrations SQLAlchemy.
# 11. Em development, cadastra as pizzas de demonstração de forma idempotente.
# 12. Em development, cria o bucket e envia as imagens ao storage selecionado.
# 13. Finaliza o bootstrap deixando o serviço pronto para execução.
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

# Variáveis exportadas pelo ambiente externo têm precedência sobre o .env.
declare -A ENVIRONMENT_OVERRIDES

for variable in \
    APP_ENV LOG_LEVEL PERSISTENCE_PROVIDER NOSQL_PROVIDER \
    NOSQL_TABLE_NAME NOSQL_ENDPOINT NOSQL_COMPARTMENT_ID \
    OBJECTSTORAGE_PROVIDER OBJECTSTORAGE_ENDPOINT OBJECTSTORAGE_BUCKET \
    OBJECTSTORAGE_ACCESS_KEY OBJECTSTORAGE_SECRET_KEY \
    OBJECTSTORAGE_COMPARTMENT_ID OCI_REGION OCI_AUTH_MODE \
    OCI_CONFIG_FILE OCI_CONFIG_PROFILE JWT_ISSUER JWT_AUDIENCE \
    JWT_JWKS_URL; do
    if [[ -v "$variable" ]]; then
        ENVIRONMENT_OVERRIDES["$variable"]="${!variable}"
    fi
done

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
NOSQL_PROVIDER=local

# Oracle NoSQL
NOSQL_TABLE_NAME=pizzas
NOSQL_ENDPOINT=http://localhost:18080
NOSQL_COMPARTMENT_ID=

# Object Storage local (MinIO)
OBJECTSTORAGE_PROVIDER=local
OBJECTSTORAGE_ENDPOINT=http://localhost:9000
OBJECTSTORAGE_BUCKET=pizza-images
OBJECTSTORAGE_ACCESS_KEY=minioadmin
OBJECTSTORAGE_SECRET_KEY=minioadmin
OBJECTSTORAGE_COMPARTMENT_ID=

# Autenticação OCI (utilizada quando um provider OCI for selecionado)
OCI_REGION=sa-saopaulo-1
OCI_AUTH_MODE=config_file
OCI_CONFIG_FILE=
OCI_CONFIG_PROFILE=DEFAULT

# JWT
JWT_ISSUER=user-service
JWT_AUDIENCE=ocipizza
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

for variable in "${!ENVIRONMENT_OVERRIDES[@]}"; do
    export "$variable=${ENVIRONMENT_OVERRIDES[$variable]}"
done

# Providers possuem valores padrão equivalentes aos definidos em Settings.
# A validação ocorre antes de iniciar qualquer recurso para evitar um
# bootstrap parcialmente executado por configuração incompleta.
export APP_ENV="${APP_ENV:-development}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"
export PERSISTENCE_PROVIDER="${PERSISTENCE_PROVIDER:-nosql}"
export NOSQL_PROVIDER="${NOSQL_PROVIDER:-local}"
export NOSQL_COMPARTMENT_ID="${NOSQL_COMPARTMENT_ID:-}"
export OBJECTSTORAGE_PROVIDER="${OBJECTSTORAGE_PROVIDER:-local}"
export OBJECTSTORAGE_COMPARTMENT_ID="${OBJECTSTORAGE_COMPARTMENT_ID:-}"
export OCI_REGION="${OCI_REGION:-sa-saopaulo-1}"
export OCI_AUTH_MODE="${OCI_AUTH_MODE:-config_file}"
export OCI_CONFIG_FILE="${OCI_CONFIG_FILE:-}"
export OCI_CONFIG_PROFILE="${OCI_CONFIG_PROFILE:-DEFAULT}"

if [ "${NOSQL_PROVIDER}" != 'local' ] && \
   [ "${NOSQL_PROVIDER}" != 'oci' ]; then
    echo "Provider NoSQL não suportado: ${NOSQL_PROVIDER}"
    echo "Utilize NOSQL_PROVIDER=local ou NOSQL_PROVIDER=oci."
    exit 1
fi

if [ "${NOSQL_PROVIDER}" != 'local' ] && \
   [ -z "${NOSQL_COMPARTMENT_ID:-}" ]; then
    echo 'Erro: NOSQL_COMPARTMENT_ID é obrigatório quando '
    echo 'NOSQL_PROVIDER for diferente de local.'
    exit 1
fi

if [ "${OBJECTSTORAGE_PROVIDER}" != 'local' ] && \
   [ "${OBJECTSTORAGE_PROVIDER}" != 'oci' ]; then
    echo "Provider Object Storage não suportado: ${OBJECTSTORAGE_PROVIDER}"
    echo "Utilize OBJECTSTORAGE_PROVIDER=local ou "\
        "OBJECTSTORAGE_PROVIDER=oci."
    exit 1
fi

# Persistência

display_step 'Inicialização da persistência'

echo "Provider de persistência configurado: ${PERSISTENCE_PROVIDER}"
echo "Provider NoSQL configurado: ${NOSQL_PROVIDER:-não utilizado}"
echo "Provider Object Storage configurado: "\
    "${OBJECTSTORAGE_PROVIDER}"

if [ "${PERSISTENCE_PROVIDER}" = "nosql" ]; then
    echo 'Inicializando a tabela Oracle NoSQL...'

    # O handle é criado pela mesma fábrica utilizada pela aplicação. Dessa
    # forma, NOSQL_PROVIDER seleciona automaticamente o backend local ou OCI.
    python <<'PYTHON'
import time

from app.config.settings import settings
from app.repositories.nosql.connection import create_nosql_handle
from borneo import TableLimits, TableRequest


table_name = settings.nosql_table_name
handle = create_nosql_handle()

try:
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

    print(f'Garantindo a tabela {table_name}...')

    # O Oracle NoSQL exige limites de capacidade durante a criação da tabela.
    # Estes valores iniciais são fixos para manter o bootstrap previsível.
    table_limits = TableLimits(
        read_units=5,
        write_units=5,
        storage_gb=1
    )

    request = (
        TableRequest()
        .set_statement(statement)
        .set_table_limits(table_limits)
    )
    result = handle.table_request(request)
    result.wait_for_completion(handle, 60000, 1000)

    # Respeita o limite de quatro operações DDL por minuto do Oracle NoSQL.
    time.sleep(16)
    print(f'Tabela {table_name} pronta para utilização.')
finally:
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
from decimal import Decimal
from uuid import UUID

from app.config.settings import settings
from app.models.pizza import Pizza, PizzaCategory
from app.repositories.nosql.connection import create_nosql_handle
from app.repositories.nosql.nosql_pizza_repository import (
    NosqlPizzaRepository
)
from app.utils.utils import now_utc


now = now_utc()

# Os identificadores fixos tornam o seed reproduzível e permitem executar o
# bootstrap novamente sem duplicar as pizzas já cadastradas.
demo_pizzas = [
    Pizza(
        id=UUID('11111111-1111-4111-8111-111111111111'),
        name='Abobrinha',
        description='Molho de tomate, mussarela, abobrinha e temperos.',
        category=PizzaCategory.VEGETARIANA,
        price=Decimal('49.90'),
        image_name='pizza-abobrinha.jpg',
        available=True,
        created_at=now,
        updated_at=now
    ),
    Pizza(
        id=UUID('22222222-2222-4222-8222-222222222222'),
        name='Bauru',
        description='Molho de tomate, mussarela, presunto e tomate.',
        category=PizzaCategory.SALGADA,
        price=Decimal('52.90'),
        image_name='pizza-bauru.jpg',
        available=True,
        created_at=now,
        updated_at=now
    ),
    Pizza(
        id=UUID('33333333-3333-4333-8333-333333333333'),
        name='Calabresa',
        description='Molho de tomate, mussarela, calabresa e cebola.',
        category=PizzaCategory.SALGADA,
        price=Decimal('49.90'),
        image_name='pizza-calabresa.jpg',
        available=True,
        created_at=now,
        updated_at=now
    ),
    Pizza(
        id=UUID('44444444-4444-4444-8444-444444444444'),
        name='Frango com Bacon',
        description=(
            'Molho de tomate, mussarela, frango desfiado e bacon.'
        ),
        category=PizzaCategory.SALGADA,
        price=Decimal('56.90'),
        image_name='pizza-fran-bacon.jpg',
        available=True,
        created_at=now,
        updated_at=now
    ),
    Pizza(
        id=UUID('55555555-5555-4555-8555-555555555555'),
        name='Frango com Mussarela',
        description='Molho de tomate, mussarela e frango desfiado.',
        category=PizzaCategory.SALGADA,
        price=Decimal('54.90'),
        image_name='pizza-frango-mussarela.jpg',
        available=True,
        created_at=now,
        updated_at=now
    ),
    Pizza(
        id=UUID('66666666-6666-4666-8666-666666666666'),
        name='Hot Dog',
        description=(
            'Molho de tomate, mussarela, salsicha, milho e batata palha.'
        ),
        category=PizzaCategory.SALGADA,
        price=Decimal('53.90'),
        image_name='pizza-hot-dog.jpg',
        available=True,
        created_at=now,
        updated_at=now
    ),
    Pizza(
        id=UUID('77777777-7777-4777-8777-777777777777'),
        name='Lombinho',
        description='Molho de tomate, mussarela e lombinho.',
        category=PizzaCategory.SALGADA,
        price=Decimal('57.90'),
        image_name='pizza-lombinho.jpg',
        available=True,
        created_at=now,
        updated_at=now
    ),
    Pizza(
        id=UUID('88888888-8888-4888-8888-888888888888'),
        name='Marguerita',
        description=(
            'Molho de tomate, mussarela, tomate, manjericão e parmesão.'
        ),
        category=PizzaCategory.VEGETARIANA,
        price=Decimal('51.90'),
        image_name='pizza-marguerita.jpg',
        available=True,
        created_at=now,
        updated_at=now
    ),
    Pizza(
        id=UUID('99999999-9999-4999-8999-999999999999'),
        name='Milho com Mussarela',
        description='Molho de tomate, mussarela e milho.',
        category=PizzaCategory.VEGETARIANA,
        price=Decimal('48.90'),
        image_name='pizza-milho-mussarela.jpg',
        available=True,
        created_at=now,
        updated_at=now
    ),
    Pizza(
        id=UUID('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'),
        name='Moda da Casa',
        description=(
            'Molho de tomate, mussarela, presunto, calabresa, milho e '
            'cebola.'
        ),
        category=PizzaCategory.SALGADA,
        price=Decimal('59.90'),
        image_name='pizza-moda-da-casa.jpg',
        available=True,
        created_at=now,
        updated_at=now
    ),
    Pizza(
        id=UUID('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'),
        name='Pepperoni',
        description='Molho de tomate, mussarela e pepperoni.',
        category=PizzaCategory.SALGADA,
        price=Decimal('58.90'),
        image_name='pizza-peperone.jpg',
        available=True,
        created_at=now,
        updated_at=now
    ),
    Pizza(
        id=UUID('cccccccc-cccc-4ccc-8ccc-cccccccccccc'),
        name='Portuguesa',
        description=(
            'Molho de tomate, mussarela, presunto, ovo, cebola e azeitonas.'
        ),
        category=PizzaCategory.SALGADA,
        price=Decimal('57.90'),
        image_name='pizza-portuguesa.jpg',
        available=True,
        created_at=now,
        updated_at=now
    )
]

if settings.persistence_provider != 'nosql':
    raise RuntimeError(
        'O seed de pizzas requer PERSISTENCE_PROVIDER=nosql.'
    )

handle = create_nosql_handle()
repository = NosqlPizzaRepository(
    handle=handle,
    table_name=settings.nosql_table_name
)

try:
    for pizza in demo_pizzas:
        existing_pizza = repository.get_by_id(pizza.id)

        if existing_pizza is not None:
            print(f'Pizza de demonstração já existe: {pizza.name}')
            continue

        repository.create(pizza)

        print(f'Pizza de demonstração criada: {pizza.name}')
finally:
    handle.close()
PYTHON

    display_step 'Inicializando o bucket e as imagens de demonstração'

    python <<'PYTHON'
import mimetypes
import os

from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

import oci
from minio import Minio
from minio.error import S3Error

from app.config.settings import settings

seeds_directory = Path('seeds')
image_paths = sorted(seeds_directory.glob('*.jpg'))

if not image_paths:
    raise RuntimeError(
        'Nenhuma imagem de demonstração foi encontrada em seeds/.'
    )

provider = settings.objectstorage_provider
bucket = settings.objectstorage_bucket

if provider == 'local':
    if not settings.objectstorage_access_key:
        raise ValueError(
            'OBJECTSTORAGE_ACCESS_KEY is required when '
            'OBJECTSTORAGE_PROVIDER is local.'
        )

    if not settings.objectstorage_secret_key:
        raise ValueError(
            'OBJECTSTORAGE_SECRET_KEY is required when '
            'OBJECTSTORAGE_PROVIDER is local.'
        )

    endpoint = urlparse(settings.objectstorage_endpoint)
    if not endpoint.netloc:
        raise ValueError('OBJECTSTORAGE_ENDPOINT is invalid.')

    client = Minio(
        endpoint.netloc,
        access_key=settings.objectstorage_access_key,
        secret_key=settings.objectstorage_secret_key,
        secure=endpoint.scheme == 'https'
    )

    # Cria o bucket local com a política privada padrão do MinIO.
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    namespace = None

elif provider == 'oci':
    if settings.oci_auth_mode == 'config_file':
        if not settings.oci_config_file:
            raise ValueError(
                'OCI_CONFIG_FILE is required when OCI_AUTH_MODE '
                'is config_file.'
            )

        config = oci.config.from_file(
            file_location=settings.oci_config_file,
            profile_name=settings.oci_config_profile or 'DEFAULT'
        )
        config['region'] = settings.oci_region
        client = oci.object_storage.ObjectStorageClient(config=config)
        region = settings.oci_region
    elif settings.oci_auth_mode == 'instance_principal':
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        region = signer.region or settings.oci_region
        client = oci.object_storage.ObjectStorageClient(
            config={'region': region},
            signer=signer
        )
    else:
        raise ValueError(
            f'Unsupported OCI authentication mode: {settings.oci_auth_mode}'
        )

    namespace = client.get_namespace().data

    # O bucket pode já existir. Só solicita o compartment quando a criação
    # realmente for necessária.
    try:
        client.get_bucket(
            namespace_name=namespace,
            bucket_name=bucket
        )
    except oci.exceptions.ServiceError as ex:
        if ex.status != 404:
            raise

        compartment_id = os.getenv('OBJECTSTORAGE_COMPARTMENT_ID')
        if not compartment_id:
            raise ValueError(
                'OBJECTSTORAGE_COMPARTMENT_ID is required to create '
                'an OCI Object Storage bucket.'
            )

        details = oci.object_storage.models.CreateBucketDetails(
            name=bucket,
            compartment_id=compartment_id
        )
        client.create_bucket(
            namespace_name=namespace,
            create_bucket_details=details
        )
else:
    raise ValueError(
        f'Unsupported Object Storage provider: {provider}'
    )

print(
    f'Bucket {bucket} pronto no provider {provider}.'
)

for image_path in image_paths:
    object_name = image_path.name

    if provider == 'local':
        try:
            client.stat_object(bucket, object_name)
            print(f'Imagem de demonstração já existe: {object_name}')
            continue
        except S3Error as ex:
            if ex.code not in {
                'NoSuchKey', 'NoSuchObject', 'NoSuchResource'
            }:
                raise
    else:
        try:
            client.head_object(
                namespace_name=namespace,
                bucket_name=bucket,
                object_name=object_name
            )
            print(f'Imagem de demonstração já existe: {object_name}')
            continue
        except oci.exceptions.ServiceError as ex:
            if ex.status != 404:
                raise

    content_type, _ = mimetypes.guess_type(image_path.name)

    if not content_type or not content_type.startswith('image/'):
        raise ValueError(
            f'Tipo de conteúdo inválido para imagem: {image_path.name}'
        )

    image_data = image_path.read_bytes()

    if provider == 'local':
        client.put_object(
            bucket_name=bucket,
            object_name=object_name,
            data=BytesIO(image_data),
            length=len(image_data),
            content_type=content_type
        )
    else:
        client.put_object(
            namespace_name=namespace,
            bucket_name=bucket,
            object_name=object_name,
            put_object_body=image_data,
            content_type=content_type
        )

    print(f'Imagem de demonstração enviada: {object_name}')
PYTHON
fi

display_step 'Bootstrap do pizza-service concluído com sucesso'

exit 0
