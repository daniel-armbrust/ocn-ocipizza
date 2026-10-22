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
#  6. Valida os providers e as configurações obrigatórias do ambiente.
#  7. Garante a tabela de pedidos e seus índices no backend NoSQL selecionado.
#  8. Verifica a existência da fila de mensagens sem criá-la.
#  9. Em development, persiste um pedido de demonstração e publica sua
#     notificação utilizando as bibliotecas da própria aplicação.
# 10. Finaliza o bootstrap deixando o serviço pronto para execução.
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
NOSQL_PROVIDER=local
NOSQL_TABLE_NAME=orders
NOSQL_ENDPOINT=http://localhost:18080
NOSQL_COMPARTMENT_ID=

# Autenticação OCI
OCI_REGION=sa-saopaulo-1
OCI_AUTH_MODE=config_file
OCI_CONFIG_FILE=
OCI_CONFIG_PROFILE=DEFAULT

# Mensageria
MESSAGING_PROVIDER=rabbitmq
QUEUE_NAME=notifications-queue

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=oci_pizza
RABBITMQ_PASSWORD=oci_pizza

# OCI Queue
OCI_QUEUE_ID=

# JWT
JWT_ISSUER=user-service
JWT_AUDIENCE=ocipizza
JWT_JWKS_URL=http://localhost:8002/.well-known/jwks.json

# Logging
LOG_LEVEL=INFO
OCI_LOG_ID=
EOF

else
    echo 'Arquivo .env já existe. Os valores atuais serão preservados.'
fi

# Versões anteriores do bootstrap criavam o .env sem as configurações de
# mensageria. Acrescenta somente valores ausentes para manter configurações
# existentes definidas pelo desenvolvedor.
ensure_env_variable() {
    local name="$1"
    local value="$2"

    if ! grep -q "^${name}=" "$ENV_FILE"; then
        printf '%s=%s\n' "$name" "$value" >> "$ENV_FILE"
        echo "Configuração ${name} adicionada ao arquivo .env."
    fi
}

ensure_env_variable 'MESSAGING_PROVIDER' 'rabbitmq'
ensure_env_variable 'QUEUE_NAME' 'notifications-queue'
ensure_env_variable 'RABBITMQ_HOST' 'localhost'
ensure_env_variable 'RABBITMQ_PORT' '5672'
ensure_env_variable 'RABBITMQ_USERNAME' 'oci_pizza'
ensure_env_variable 'RABBITMQ_PASSWORD' 'oci_pizza'
ensure_env_variable 'NOSQL_PROVIDER' 'local'
ensure_env_variable 'NOSQL_COMPARTMENT_ID' ''
ensure_env_variable 'OCI_REGION' 'sa-saopaulo-1'
ensure_env_variable 'OCI_AUTH_MODE' 'config_file'
ensure_env_variable 'OCI_CONFIG_FILE' ''
ensure_env_variable 'OCI_CONFIG_PROFILE' 'DEFAULT'
ensure_env_variable 'OCI_QUEUE_ID' ''

# Exporta as configurações para que o módulo Settings e o cliente Oracle
# NoSQL compartilhem exatamente os mesmos valores durante o bootstrap.
echo 'Carregando configurações do ambiente...'

# Variáveis exportadas pelo ambiente externo têm precedência sobre o .env.
# Preserva esses valores antes do carregamento e restaura-os em seguida.
declare -A ENVIRONMENT_OVERRIDES

for variable in \
    APP_NAME APP_ENV DEBUG LOG_LEVEL \
    PERSISTENCE_PROVIDER NOSQL_PROVIDER NOSQL_TABLE_NAME NOSQL_ENDPOINT \
    NOSQL_COMPARTMENT_ID OCI_REGION OCI_AUTH_MODE OCI_CONFIG_FILE \
    OCI_CONFIG_PROFILE MESSAGING_PROVIDER QUEUE_NAME OCI_QUEUE_ID \
    RABBITMQ_HOST RABBITMQ_PORT RABBITMQ_USERNAME RABBITMQ_PASSWORD \
    JWT_ISSUER JWT_AUDIENCE JWT_JWKS_URL OCI_LOG_ID; do
    if [[ -v "$variable" ]]; then
        ENVIRONMENT_OVERRIDES["$variable"]="${!variable}"
    fi
done

set -a
source "$ENV_FILE"
set +a

for variable in "${!ENVIRONMENT_OVERRIDES[@]}"; do
    export "$variable=${ENVIRONMENT_OVERRIDES[$variable]}"
done

export NOSQL_PROVIDER="${NOSQL_PROVIDER:-local}"
export MESSAGING_PROVIDER="${MESSAGING_PROVIDER:-rabbitmq}"

# Quando o modo config_file é utilizado sem um caminho explícito, usa o
# arquivo padrão criado pelo OCI CLI no diretório pessoal do usuário.
export OCI_CONFIG_FILE="${OCI_CONFIG_FILE:-${HOME}/.oci/config}"

if [ "${NOSQL_PROVIDER}" != 'local' ] && \
   [ "${NOSQL_PROVIDER}" != 'oci' ]; then
    echo "Provider NoSQL não suportado: ${NOSQL_PROVIDER}"
    echo 'Utilize NOSQL_PROVIDER=local ou NOSQL_PROVIDER=oci.'
    exit 1
fi

if [ "${NOSQL_PROVIDER}" = 'oci' ] && \
   [ -z "${NOSQL_COMPARTMENT_ID:-}" ]; then
    echo 'Erro: NOSQL_COMPARTMENT_ID é obrigatório quando '
    echo 'NOSQL_PROVIDER=oci.'
    exit 1
fi

if [ "${MESSAGING_PROVIDER}" != 'rabbitmq' ] && \
   [ "${MESSAGING_PROVIDER}" != 'oci_queue' ]; then
    echo "Provider de mensageria não suportado: ${MESSAGING_PROVIDER}"
    echo 'Utilize MESSAGING_PROVIDER=rabbitmq ou MESSAGING_PROVIDER=oci_queue.'
    exit 1
fi

if [ "${MESSAGING_PROVIDER}" = 'rabbitmq' ]; then
    for required_variable in \
        RABBITMQ_HOST RABBITMQ_PORT RABBITMQ_USERNAME RABBITMQ_PASSWORD; do
        if [ -z "${!required_variable:-}" ]; then
            echo "Erro: ${required_variable} é obrigatório para RabbitMQ."
            exit 1
        fi
    done
fi

if [ "${NOSQL_PROVIDER}" = 'oci' ] || \
   [ "${MESSAGING_PROVIDER}" = 'oci_queue' ]; then
    if [ "${OCI_AUTH_MODE}" != 'config_file' ] && \
       [ "${OCI_AUTH_MODE}" != 'instance_principal' ]; then
        echo "Modo de autenticação OCI não suportado: ${OCI_AUTH_MODE}"
        echo 'Utilize OCI_AUTH_MODE=config_file ou '
        echo 'OCI_AUTH_MODE=instance_principal.'
        exit 1
    fi
fi

if [ "${OCI_AUTH_MODE}" = 'config_file' ] && \
   { [ "${NOSQL_PROVIDER}" = 'oci' ] || \
     [ "${MESSAGING_PROVIDER}" = 'oci_queue' ]; } && \
   [ -z "${OCI_CONFIG_FILE:-}" ]; then
    echo 'Erro: OCI_CONFIG_FILE é obrigatório quando um provider OCI '
    echo 'utiliza OCI_AUTH_MODE=config_file.'
    exit 1
fi

if [ "${OCI_AUTH_MODE}" = 'config_file' ] && \
   { [ "${NOSQL_PROVIDER}" = 'oci' ] || \
     [ "${MESSAGING_PROVIDER}" = 'oci_queue' ]; } && \
   [ ! -f "${OCI_CONFIG_FILE}" ]; then
    echo "Erro: arquivo de configuração OCI não encontrado: ${OCI_CONFIG_FILE}"
    exit 1
fi

if [ "${MESSAGING_PROVIDER}" = 'rabbitmq' ]; then
    display_step 'Verificando a fila RabbitMQ'

    python <<'PYTHON'
import os

import pika


credentials = pika.PlainCredentials(
    os.environ['RABBITMQ_USERNAME'],
    os.environ['RABBITMQ_PASSWORD']
)
parameters = pika.ConnectionParameters(
    host=os.environ['RABBITMQ_HOST'],
    port=int(os.environ['RABBITMQ_PORT']),
    credentials=credentials
)

connection = pika.BlockingConnection(parameters)
try:
    channel = connection.channel()

    # O modo passivo somente consulta a fila; ele não a declara nem cria.
    channel.queue_declare(
        queue=os.environ['QUEUE_NAME'],
        passive=True
    )
finally:
    connection.close()

print(f"Fila RabbitMQ existente: {os.environ['QUEUE_NAME']}")
PYTHON
else
    display_step 'Verificando a fila OCI Queue'

    if [ -z "${OCI_QUEUE_ID:-}" ]; then
        echo 'Erro: OCI_QUEUE_ID é obrigatório quando '
        echo 'MESSAGING_PROVIDER=oci_queue.'
        exit 1
    fi

    python <<'PYTHON'
import os

import oci
from oci.auth.signers import InstancePrincipalsSecurityTokenSigner


if os.environ['OCI_AUTH_MODE'] == 'config_file':
    config = oci.config.from_file(
        file_location=os.environ['OCI_CONFIG_FILE'],
        profile_name=os.environ.get('OCI_CONFIG_PROFILE')
    )
    config['region'] = os.environ['OCI_REGION']
    queue_admin_client = oci.queue.QueueAdminClient(config=config)
else:
    signer = InstancePrincipalsSecurityTokenSigner()
    queue_admin_client = oci.queue.QueueAdminClient(
        config={'region': signer.region},
        signer=signer
    )

# Consulta somente os metadados da fila. Nenhuma fila é criada pelo script.
queue_admin_client.get_queue(
    queue_id=os.environ['OCI_QUEUE_ID']
)

print(f"Fila OCI Queue existente: {os.environ['OCI_QUEUE_ID']}")
PYTHON
fi

display_step 'Inicialização da persistência'

echo "Provider de persistência configurado: ${PERSISTENCE_PROVIDER}"

if [ "${PERSISTENCE_PROVIDER}" != 'nosql' ]; then
    echo "Provider de persistência não suportado pelo bootstrap: ${PERSISTENCE_PROVIDER}"
    exit 1
fi

echo 'Inicializando persistência Oracle NoSQL...'

python <<'PYTHON'
import re
import time

from app.config.settings import settings
from borneo import TableLimits, TableRequest

from app.repositories.nosql.connection import create_nosql_handle


table_name = settings.nosql_table_name

# O Oracle NoSQL limita o tenant a quatro operações DDL por minuto. O
# bootstrap cria a tabela e vários índices, portanto cada operação aguarda
# este intervalo antes de permitir a próxima submissão.
DDL_INTERVAL_SECONDS = 16

# O nome participa diretamente das instruções DDL. A validação impede que um
# valor arbitrário vindo do ambiente altere a estrutura dos comandos.
if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', table_name):
    raise ValueError('NOSQL_TABLE_NAME possui um identificador inválido.')

handle = create_nosql_handle()


def execute_ddl(
    statement: str,
    description: str,
    table_limits: TableLimits | None = None
) -> None:
    """
    Executa uma instrução DDL e aguarda sua conclusão no Oracle NoSQL.

    Args:
        statement: Instrução DDL que será submetida ao banco de dados.
        description: Mensagem que identifica a operação em andamento.
        table_limits: Limites de capacidade utilizados na criação da tabela.

    Returns:
        None.

    Raises:
        borneo.NoSQLException: Quando o Oracle NoSQL rejeita a instrução ou
            não consegue concluí-la dentro do período de espera.
    """

    print(description)
    request = TableRequest().set_statement(statement)

    if table_limits is not None:
        request.set_table_limits(table_limits)

    result = handle.table_request(request)
    result.wait_for_completion(handle, 60000, 1000)

    # Mantém as operações abaixo do limite de DDL do tenant, inclusive quando
    # a instrução utiliza IF NOT EXISTS e a estrutura já está criada.
    time.sleep(DDL_INTERVAL_SECONDS)


# O UUID do pedido já é único. Usá-lo sozinho evita ultrapassar o limite de
# 64 caracteres que seria excedido ao combinar dois UUIDs na chave primária.
table_statement = f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
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
        PRIMARY KEY(id)
    )
'''

# O Oracle NoSQL permite no máximo cinco índices por tabela. A seleção abaixo
# cobre as consultas administrativas, por usuário e por idempotência sem
# ultrapassar esse limite.
index_statements = (
    (
        f'CREATE INDEX IF NOT EXISTS idx_orders_id ON {table_name}(id)',
        'Criando índice para consulta administrativa por pedido...'
    ),
    (
        f'CREATE INDEX IF NOT EXISTS idx_orders_user_created_at '
        f'ON {table_name}(user_id, created_at)',
        'Criando índice para ordenar os pedidos de um usuário...'
    ),
    (
        f'CREATE INDEX IF NOT EXISTS idx_orders_idempotency '
        f'ON {table_name}(idempotency_key)',
        'Criando índice para consulta por idempotência...'
    ),
    (
        f'CREATE INDEX IF NOT EXISTS idx_orders_status '
        f'ON {table_name}(status)',
        'Criando índice para consulta dos pedidos por status...'
    ),
    (
        f'CREATE INDEX IF NOT EXISTS idx_orders_created_at '
        f'ON {table_name}(created_at)',
        'Criando índice para ordenar todos os pedidos...'
    )
)

# O Oracle NoSQL exige limites de capacidade durante a criação da tabela.
# Estes valores iniciais são fixos para manter o bootstrap previsível.
table_limits = TableLimits(
    read_units=5,
    write_units=5,
    storage_gb=1
)

try:
    execute_ddl(
        table_statement,
        f'Garantindo a tabela {table_name}...',
        table_limits=table_limits
    )

    for statement, description in index_statements:
        execute_ddl(statement, description)
finally:
    handle.close()

print(f'Tabela {table_name} e índices prontos para utilização.')
PYTHON

if [ "${APP_ENV}" = 'development' ]; then
    display_step 'Criando pedido e publicando notificação de demonstração'

    python <<'PYTHON'
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from app.config.settings import settings
from app.dependencies.messaging import get_message_publisher
from app.messaging.message_publisher import MessagePublisher
from app.models.order import (
    CustomerSnapshot,
    DeliveryAddressSnapshot,
    Order,
    OrderItem,
    OrderStatus,
    PaymentStatus
)
from app.repositories.nosql.connection import create_nosql_handle
from app.repositories.nosql.nosql_order_repository import (
    NosqlOrderRepository
)
from app.services.order_email_service import OrderEmailService


demo_user_id = UUID('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa')
demo_order_id = UUID('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb')
demo_idempotency_key = UUID('cccccccc-cccc-4ccc-8ccc-cccccccccccc')
now = datetime.now(timezone.utc)

demo_order = Order(
    id=demo_order_id,
    user_id=demo_user_id,
    customer=CustomerSnapshot(
        name='Usuário de demonstração',
        email='demo@example.com',
        whatsapp='15999999999'
    ),
    delivery_address=DeliveryAddressSnapshot(
        zip_code='18000001',
        street='Rua de Demonstração',
        number='100',
        complement=None,
        neighborhood='Centro',
        city='Sorocaba',
        state='SP'
    ),
    items=[
        OrderItem(
            pizza_id=UUID('11111111-1111-4111-8111-111111111111'),
            name='Abobrinha',
            quantity=1,
            unit_price=Decimal('49.90'),
            subtotal=Decimal('49.90')
        )
    ],
    subtotal=Decimal('49.90'),
    delivery_fee=Decimal('5.00'),
    total=Decimal('54.90'),
    status=OrderStatus.RECEIVED,
    payment_status=PaymentStatus.PAID,
    idempotency_key=demo_idempotency_key,
    created_at=now,
    updated_at=now
)

handle = create_nosql_handle()
repository = NosqlOrderRepository(
    handle=handle,
    table_name=settings.nosql_table_name,
    use_client_side_sort=settings.app_env == 'development'
)

try:
    existing_order = repository.get_by_id(
        order_id=demo_order.id,
        user_id=demo_order.user_id
    )

    if existing_order is not None:
        print(f'Pedido de demonstração já existe: {demo_order.id}')
    else:
        # Persiste o modelo pelo mesmo repositório usado pela aplicação.
        repository.create(demo_order)
        print(f'Pedido de demonstração criado: {demo_order.id}')

        # Publica a mensagem pela mesma abstração utilizada pela API. Assim,
        # RabbitMQ e OCI Queue são exercitados pelo provider selecionado.
        message_publisher: MessagePublisher = get_message_publisher()
        order_email_service = OrderEmailService(message_publisher)
        order_email_service.send_order_received(demo_order)
        print('Notificação de pedido de demonstração publicada.')
finally:
    handle.close()
PYTHON
fi

display_step 'Bootstrap do order-service concluído com sucesso'

exit 0
