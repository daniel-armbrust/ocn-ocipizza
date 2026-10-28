#!/bin/bash

#
# bootstrap.sh - notification-service
#
# Este script prepara o ambiente de desenvolvimento local do
# notification-service.
#
# Etapas executadas:
#
#  1. Valida os requisitos necessários para executar o bootstrap.
#  2. Cria e ativa o ambiente virtual Python.
#  3. Atualiza o pip e instala as dependências do serviço.
#  4. Cria o arquivo .env local, caso ele ainda não exista.
#  5. Carrega e valida as configurações dos providers.
#  6. Cria ou valida a fila OCI Queue quando esse provider estiver configurado.
#  7. Garante o remetente no OCI Email Delivery e inicializa o provider de e-mail.
#  8. Finaliza o bootstrap deixando o worker pronto para execução.
#
# Uso:
#
#     ./bootstrap.sh
#
# O script deve ser executado a partir do diretório raiz do
# notification-service.
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

display_step 'Iniciando o bootstrap do notification-service'

if [ ! -f 'requirements.txt' ]; then
    echo 'Erro: requirements.txt não encontrado.'
    echo 'Execute este script a partir do diretório raiz do notification-service.'
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

source "$VENV_DIR/bin/activate"

display_step 'Atualizando o pip'
python -m pip install --upgrade pip

display_step 'Instalando as dependências Python'
python -m pip install --no-cache-dir -r requirements.txt

display_step 'Configurando o arquivo .env do ambiente local'

if [ ! -f "$ENV_FILE" ]; then
    echo 'Criando arquivo .env para desenvolvimento local...'

    cat > "$ENV_FILE" <<'EOF'
APP_NAME=notification-service
APP_ENV=development
DEBUG=true

# URL pública utilizada na construção dos links dos e-mails.
SITE_URL=http://localhost:8010

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
QUEUE_COMPARTMENT_ID=

# E-mail
EMAIL_PROVIDER=smtp
EMAIL_TEMPLATES_PATH=app/templates/emails

# SMTP local com Mailpit.
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=false
SMTP_EMAIL_SENDER=no-reply@ocipizza.local

# OCI Email Delivery.
OCI_EMAIL_DELIVERY_COMPARTMENT_ID=
OCI_EMAIL_SENDER_NAME="OCI Pizza"

# Autenticação dos serviços OCI.
OCI_REGION=sa-saopaulo-1
OCI_AUTH_MODE=
OCI_CONFIG_FILE=
OCI_CONFIG_PROFILE=DEFAULT

# Intervalos do worker, em segundos.
NOTIFICATION_POLL_INTERVAL=5.0
NOTIFICATION_RETRY_INTERVAL=10.0

# Logging.
LOG_LEVEL=INFO
OCI_LOG_ID=
EOF
else
    echo 'Arquivo .env já existe. Os valores atuais serão preservados.'
fi

# Acrescenta somente configurações ausentes, preservando valores definidos
# manualmente pelo desenvolvedor.
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
ensure_env_variable 'OCI_QUEUE_ID' ''
ensure_env_variable 'QUEUE_COMPARTMENT_ID' ''
ensure_env_variable 'EMAIL_PROVIDER' 'smtp'
ensure_env_variable 'SMTP_HOST' 'localhost'
ensure_env_variable 'SMTP_PORT' '1025'
ensure_env_variable 'SMTP_EMAIL_SENDER' 'no-reply@ocipizza.local'
ensure_env_variable 'OCI_EMAIL_DELIVERY_COMPARTMENT_ID' ''
ensure_env_variable 'OCI_EMAIL_SENDER_NAME' 'OCI Pizza'
ensure_env_variable 'OCI_REGION' 'sa-saopaulo-1'
ensure_env_variable 'OCI_AUTH_MODE' ''
ensure_env_variable 'OCI_CONFIG_FILE' ''
ensure_env_variable 'OCI_CONFIG_PROFILE' 'DEFAULT'

# Corrige o valor padrão de versões anteriores do .env que não protegiam o
# espaço do nome do remetente, evitando que o shell interprete "Pizza" como
# um comando durante o carregamento das configurações.
if grep -q '^OCI_EMAIL_SENDER_NAME=OCI Pizza$' "$ENV_FILE"; then
    sed -i 's/^OCI_EMAIL_SENDER_NAME=OCI Pizza$/OCI_EMAIL_SENDER_NAME="OCI Pizza"/' \
        "$ENV_FILE"
fi

echo 'Carregando configurações do ambiente...'

# Variáveis exportadas pelo ambiente externo devem ter precedência sobre o
# arquivo .env. Os valores são preservados antes do carregamento e restaurados
# depois dele para manter esse comportamento também quando o .env já existe.
declare -A ENVIRONMENT_OVERRIDES

for variable in \
    APP_NAME APP_ENV DEBUG SITE_URL \
    MESSAGING_PROVIDER QUEUE_NAME \
    RABBITMQ_HOST RABBITMQ_PORT RABBITMQ_USERNAME RABBITMQ_PASSWORD \
    OCI_QUEUE_ID QUEUE_COMPARTMENT_ID \
    EMAIL_PROVIDER EMAIL_TEMPLATES_PATH \
    SMTP_HOST SMTP_PORT SMTP_USERNAME SMTP_PASSWORD SMTP_USE_TLS \
    SMTP_EMAIL_SENDER OCI_EMAIL_DELIVERY_COMPARTMENT_ID \
    OCI_EMAIL_SENDER_NAME OCI_REGION OCI_AUTH_MODE OCI_CONFIG_FILE \
    OCI_CONFIG_PROFILE NOTIFICATION_POLL_INTERVAL \
    NOTIFICATION_RETRY_INTERVAL LOG_LEVEL OCI_LOG_ID; do
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

export MESSAGING_PROVIDER="${MESSAGING_PROVIDER:-rabbitmq}"
export EMAIL_PROVIDER="${EMAIL_PROVIDER:-smtp}"

if [ "${MESSAGING_PROVIDER}" != 'rabbitmq' ] && \
   [ "${MESSAGING_PROVIDER}" != 'oci_queue' ]; then
    echo "Provider de mensageria não suportado: ${MESSAGING_PROVIDER}"
    echo 'Utilize MESSAGING_PROVIDER=rabbitmq ou MESSAGING_PROVIDER=oci_queue.'
    exit 1
fi

if [ "${EMAIL_PROVIDER}" != 'smtp' ] && \
   [ "${EMAIL_PROVIDER}" != 'oci' ]; then
    echo "Provider de e-mail não suportado: ${EMAIL_PROVIDER}"
    echo 'Utilize EMAIL_PROVIDER=smtp ou EMAIL_PROVIDER=oci.'
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

if [ "${MESSAGING_PROVIDER}" = 'oci_queue' ] && \
   [ -z "${QUEUE_COMPARTMENT_ID:-}" ]; then
    echo 'Erro: QUEUE_COMPARTMENT_ID é obrigatório quando '
    echo 'MESSAGING_PROVIDER=oci_queue.'
    exit 1
fi

if [ "${EMAIL_PROVIDER}" = 'smtp' ]; then
    if [ -z "${SMTP_HOST:-}" ] || [ -z "${SMTP_PORT:-}" ]; then
        echo 'Erro: SMTP_HOST e SMTP_PORT são obrigatórios para SMTP.'
        exit 1
    fi

    if [ -z "${SMTP_EMAIL_SENDER:-}" ]; then
        echo 'Erro: SMTP_EMAIL_SENDER é obrigatório para SMTP.'
        exit 1
    fi
fi

if [ "${EMAIL_PROVIDER}" = 'oci' ]; then
    if [ -z "${OCI_EMAIL_DELIVERY_COMPARTMENT_ID:-}" ]; then
        echo 'Erro: OCI_EMAIL_DELIVERY_COMPARTMENT_ID é obrigatório quando '
        echo 'EMAIL_PROVIDER=oci.'
        exit 1
    fi

    if [ -z "${SMTP_EMAIL_SENDER:-}" ]; then
        echo 'Erro: SMTP_EMAIL_SENDER deve conter o remetente aprovado '
        echo 'quando EMAIL_PROVIDER=oci.'
        exit 1
    fi
fi

if [ "${MESSAGING_PROVIDER}" = 'oci_queue' ] || \
   [ "${EMAIL_PROVIDER}" = 'oci' ]; then
    if [ "${OCI_AUTH_MODE}" != 'config_file' ] && \
       [ "${OCI_AUTH_MODE}" != 'instance_principal' ]; then
        echo "Modo de autenticação OCI não suportado: ${OCI_AUTH_MODE}"
        echo 'Utilize OCI_AUTH_MODE=config_file ou '
        echo 'OCI_AUTH_MODE=instance_principal.'
        exit 1
    fi
fi

if [ "${OCI_AUTH_MODE}" = 'config_file' ] && \
   { [ "${MESSAGING_PROVIDER}" = 'oci_queue' ] || \
     [ "${EMAIL_PROVIDER}" = 'oci' ]; } && \
   [ -z "${OCI_CONFIG_FILE:-}" ]; then
    echo 'Erro: OCI_CONFIG_FILE é obrigatório quando um provider OCI '
    echo 'utiliza OCI_AUTH_MODE=config_file.'
    exit 1
fi

if [ "${MESSAGING_PROVIDER}" = 'oci_queue' ]; then
    display_step 'Criando ou validando a fila OCI Queue'

    python <<'PYTHON'
import os
import time
from pathlib import Path

import oci
import oci.queue
import oci.queue.models
from oci.auth.signers import InstancePrincipalsSecurityTokenSigner


queue_name = os.environ['QUEUE_NAME']
compartment_id = os.environ['QUEUE_COMPARTMENT_ID']
queue_id = os.environ.get('OCI_QUEUE_ID')

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

if queue_id:
    # Valida a fila informada sem criar uma segunda fila.
    queue_admin_client.get_queue(queue_id=queue_id)
else:
    queue_collection = queue_admin_client.list_queues(
        compartment_id=compartment_id,
        display_name=queue_name
    ).data

    # O SDK retorna QueueCollection; os itens ficam no atributo `items`.
    if queue_collection.items:
        queue_id = queue_collection.items[0].id
    else:
        create_response = queue_admin_client.create_queue(
            oci.queue.models.CreateQueueDetails(
                compartment_id=compartment_id,
                display_name=queue_name
            )
        )

        work_request_id = create_response.headers.get(
            'opc-work-request-id'
        )

        if not work_request_id:
            raise RuntimeError(
                'OCI Queue creation did not return a work request ID.'
            )

        # A criação de uma fila OCI é assíncrona e a resposta inicial não
        # possui `data`. Aguarda a conclusão para obter o OCID criado.
        for _ in range(60):
            work_request = queue_admin_client.get_work_request(
                work_request_id=work_request_id
            ).data

            if work_request.status == 'SUCCEEDED':
                resources = work_request.resources or []
                queue_resources = [
                    resource
                    for resource in resources
                    if resource.identifier
                ]

                if not queue_resources:
                    raise RuntimeError(
                        'OCI Queue creation completed without a queue ID.'
                    )

                queue_id = queue_resources[0].identifier
                break

            if work_request.status in {'FAILED', 'CANCELED'}:
                raise RuntimeError(
                    'OCI Queue creation failed: '
                    f'{work_request.status}.'
                )

            time.sleep(2)
        else:
            raise TimeoutError(
                'Timed out waiting for OCI Queue creation.'
            )

env_file = Path('.env')
lines = env_file.read_text(encoding='utf-8').splitlines()
updated = False

for index, line in enumerate(lines):
    if line.startswith('OCI_QUEUE_ID='):
        lines[index] = f'OCI_QUEUE_ID={queue_id}'
        updated = True
        break

if not updated:
    lines.append(f'OCI_QUEUE_ID={queue_id}')

env_file.write_text(
    '\n'.join(lines) + '\n',
    encoding='utf-8'
)

print(f'Fila OCI Queue pronta: {queue_id}')
PYTHON

    set -a
    source "$ENV_FILE"
    set +a
fi

display_step 'Preparando o provider de e-mail'

if [ "${EMAIL_PROVIDER}" = 'oci' ]; then
    display_step 'Garantindo o remetente no OCI Email Delivery'

    python <<'PYTHON'
import os

import oci.email
import oci.email.models
from oci.auth.signers import InstancePrincipalsSecurityTokenSigner


if os.environ['OCI_AUTH_MODE'] == 'config_file':
    config = oci.config.from_file(
        file_location=os.environ['OCI_CONFIG_FILE'],
        profile_name=os.environ.get('OCI_CONFIG_PROFILE')
    )
    config['region'] = os.environ['OCI_REGION']
    email_admin_client = oci.email.EmailClient(config=config)
else:
    signer = InstancePrincipalsSecurityTokenSigner()
    email_admin_client = oci.email.EmailClient(
        config={'region': signer.region},
        signer=signer
    )

compartment_id = os.environ['OCI_EMAIL_DELIVERY_COMPARTMENT_ID']
sender_email = os.environ['SMTP_EMAIL_SENDER']

# Consulta os remetentes existentes para tornar o bootstrap idempotente.
senders = email_admin_client.list_senders(
    compartment_id=compartment_id
).data.items

sender = next(
    (
        item for item in senders
        if item.email_address.lower() == sender_email.lower()
    ),
    None
)

if sender is None:
    # Cria somente o remetente; a verificação do domínio permanece sob
    # responsabilidade da configuração do OCI Email Delivery e do DNS.
    sender = email_admin_client.create_sender(
        oci.email.models.CreateSenderDetails(
            compartment_id=compartment_id,
            email_address=sender_email
        )
    ).data
    print(f'Remetente OCI criado: {sender.email_address}')
else:
    print(f'Remetente OCI já existe: {sender.email_address}')
PYTHON
fi

python <<'PYTHON'
import oci.email_data_plane

from app.dependencies.clients import get_email_sender


# A fábrica da aplicação valida e inicializa o provider SMTP ou OCI Email
# Delivery com as configurações carregadas pelo próprio serviço.
email_sender = get_email_sender()

print(
    'Provider de e-mail preparado: '
    f'{email_sender.__class__.__name__}'
)
PYTHON

display_step 'Bootstrap do notification-service concluído com sucesso'

exit 0
