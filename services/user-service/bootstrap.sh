#!/bin/bash

#
# bootstrap.sh
#
# Script de inicialização do ambiente de desenvolvimento do user-service.
#
# Este script prepara automaticamente todos os componentes necessários para
# executar o serviço em um ambiente local de desenvolvimento.
#
# Etapas executadas:
#
# 1. Verifica se o script está sendo executado a partir do diretório raiz
#    do user-service.
#
# 2. Define as configurações utilizadas pelo ambiente local de desenvolvimento,
#    incluindo host, porta, usuário e senha do MySQL.
#
# 3. Verifica se o Python 3.11 está disponível.
#
# 4. Verifica se o ambiente virtual Python (.venv) já existe e cria um novo
#    ambiente quando necessário.
#
# 5. Ativa o ambiente virtual Python.
#
# 6. Atualiza o pip.
#
# 7. Instala as dependências Python declaradas em requirements.txt.
#
# 8. Verifica se o arquivo .env existe e, quando necessário, cria o arquivo
#    com as configurações padrão do ambiente de desenvolvimento.
#
# 9. Verifica os clientes do MySQL e aguarda o servidor ficar disponível.
#
# 10. Cria o banco de dados "users" e o usuário utilizado pelo serviço,
#     caso ainda não existam.
#
# 11. Verifica a estrutura do Alembic e a inicializa quando necessário.
#
# 12. Verifica se existem migrations e gera a migration inicial quando
#     nenhuma migration estiver disponível.
#
# 13. Aplica todas as migrations e atualiza o schema do banco de dados.
#
# 14. Cria os usuários de demonstração e o usuário administrador que ainda
#     não estiverem cadastrados.
#
# 15. Exibe uma mensagem indicando a conclusão do processo.
#
# Este script foi desenvolvido exclusivamente para o ambiente de desenvolvimento.
# Ele utiliza configurações simplificadas, incluindo credenciais locais do
# MySQL, que não devem ser utilizadas em ambientes de produção.
#
# Uso:
#
#     ./bootstrap.sh
#
# O script deve ser executado a partir do diretório raiz do user-service.
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

MYSQL_HOST='127.0.0.1'
MYSQL_PORT='13306'

MYSQL_ROOT_USER='root'
MYSQL_ROOT_PASSWORD='root'

DATABASE_NAME='users'
DATABASE_USER='user_service'
DATABASE_PASSWORD='user_service'

VENV_DIR='.venv'
ENV_FILE='.env'

display_step 'Iniciando o bootstrap do user-service'

# Verifica se o script está sendo executado na raiz do user-service.

if [ ! -f 'requirements.txt' ]; then
    echo 'Erro: requirements.txt não encontrado.'
    echo 'Execute este script a partir do diretório raiz do user-service.'
    exit 1
fi

# Verifica se o Python 3.11 está disponível.

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

# Ativa o ambiente virtual Python.
source "$VENV_DIR/bin/activate"

display_step 'Atualizando o pip'
python -m pip install --upgrade pip

display_step 'Instalando as dependências Python'
python -m pip install --no-cache-dir -r requirements.txt

display_step 'Configurando o arquivo .env do ambiente local'

if [ ! -f "$ENV_FILE" ]; then

    echo 'Criando arquivo .env de desenvolvimento...'

    cat > "$ENV_FILE" <<EOF
APP_NAME=user-service
APP_ENV=development
DEBUG=true

PERSISTENCE_PROVIDER=sqlalchemy

DATABASE_URL=mysql+pymysql://${DATABASE_USER}:${DATABASE_PASSWORD}@${MYSQL_HOST}:${MYSQL_PORT}/${DATABASE_NAME}

MESSAGING_PROVIDER=rabbitmq

RABBITMQ_HOST=127.0.0.1
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=oci_pizza
RABBITMQ_PASSWORD=oci_pizza
RABBITMQ_QUEUE_NAME=notifications

JWT_ISSUER=user-service
JWT_AUDIENCE=oci-pizza
EOF

else
    echo 'Arquivo .env já existe. Nenhuma alteração será realizada.'
fi

# Verifica se os clientes do MySQL estão disponíveis.

if ! command -v mysql >/dev/null 2>&1; then
    echo 'Erro: cliente MySQL não foi encontrado.'
    exit 1
fi

if ! command -v mysqladmin >/dev/null 2>&1; then
    echo 'Erro: mysqladmin não foi encontrado.'
    exit 1
fi

display_step 'Aguardando o servidor MySQL ficar disponível'

until mysqladmin \
    -h "$MYSQL_HOST" \
    -P "$MYSQL_PORT" \
    -u "$MYSQL_ROOT_USER" \
    -p"$MYSQL_ROOT_PASSWORD" \
    ping \
    --silent
do
    echo 'MySQL ainda não está disponível.'
    sleep 2
done

echo 'MySQL disponível.'

# Configura o banco de dados utilizado pelo user-service.

mysql \
    -h "$MYSQL_HOST" \
    -P "$MYSQL_PORT" \
    -u "$MYSQL_ROOT_USER" \
    -p"$MYSQL_ROOT_PASSWORD" \
    -e "
        CREATE DATABASE IF NOT EXISTS ${DATABASE_NAME};

        CREATE USER IF NOT EXISTS
            '${DATABASE_USER}'@'%'
            IDENTIFIED BY '${DATABASE_PASSWORD}';

        GRANT ALL PRIVILEGES
            ON ${DATABASE_NAME}.*
            TO '${DATABASE_USER}'@'%';

        FLUSH PRIVILEGES;
    "

display_step 'Verificando a estrutura do Alembic'

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

from app.repositories.orm.user_orm import UserORM
from app.repositories.orm.email_confirmation_token_orm import EmailConfirmationTokenORM
from app.repositories.orm.password_reset_token_orm import PasswordResetTokenORM
from app.repositories.orm.refresh_token_orm import RefreshTokenORM
from app.repositories.orm.password_history_orm import PasswordHistoryORM

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


#
# Substitui a URL configurada no alembic.ini pela DATABASE_URL
# utilizada pela própria aplicação.
#

config.set_main_option(
    'sqlalchemy.url',
    settings.database_url,
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
            'paramstyle': 'named',
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
            {},
        ),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
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

python <<'PYTHON'

import uuid

from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config.settings import settings

from app.repositories.orm.user_orm import UserORM
from app.repositories.orm.email_confirmation_token_orm import EmailConfirmationTokenORM
from app.repositories.orm.password_reset_token_orm import PasswordResetTokenORM
from app.repositories.orm.refresh_token_orm import RefreshTokenORM
from app.repositories.orm.password_history_orm import PasswordHistoryORM

from app.services.user_password_service import UserPasswordService

from app.utils.utils import now_utc
from app.utils.utils import uuid_to_bin

#
# Usuários utilizados exclusivamente para demonstração e testes locais.
#
# Os UUIDs são fixos para permitir que outros exemplos e serviços façam
# referência aos mesmos usuários de maneira determinística.
#

DEMO_USERS = [
    {
        'id': uuid.UUID(
            '11111111-1111-4111-8111-111111111111'
        ),
        'full_name': 'Maria Oliveira',
        'email': 'maria.oliveira@example.com',
        'confirmed': True,
        'is_admin': False,
        'whatsapp': '+5511999999999',
        'password': 'DemoPassword123!'
    },
    {
        'id': uuid.UUID(
            '22222222-2222-4222-8222-222222222222'
        ),
        'full_name': 'Joao Silva',
        'email': 'joao.silva@example.com',
        'confirmed': False,
        'is_admin': False,
        'whatsapp': '+5511988888888',
        'password': 'DemoPassword123!'
    },
    {
        'id': uuid.UUID(
            '33333333-3333-4333-8333-333333333333'
        ),
        'full_name': 'Rita de Cássia',
        'email': 'rita.cassia@example.com',
        'confirmed': True,
        'is_admin': False,
        'whatsapp': '+5511977777777',
        'password': 'DemoPassword123!'
    }
]

ADMIN_USER = {
    'id': uuid.UUID('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'),
    'full_name': 'Administrador',
    'email': 'admin@ocipizza.com.br',
    'confirmed': True,
    'whatsapp': '+5511900000000',
    'password': 'AdminPassword123!',
    'is_admin': True
}

USERS_TO_SEED = [
    ADMIN_USER,
    *DEMO_USERS,
]

#
# Cria uma conexão SQLAlchemy utilizando a mesma DATABASE_URL
# configurada para a aplicação.
#
engine = create_engine(
    settings.database_url
)

#
# O serviço de senha é utilizado para garantir que nenhuma senha
# seja armazenada em texto puro no banco de dados.
#
password_service = UserPasswordService(
    user_repository=None,
    password_reset_token_repository=None,
    #password_history_repository,
    token_service=None,
    user_email_service=None,
    unit_of_work=None
)

with Session(engine) as session:
    for seed_user in USERS_TO_SEED:

        #
        # Verifica se o usuário já existe.
        #
        # Isso torna o processo de seed idempotente e permite executar
        # o bootstrap novamente sem duplicar usuários.
        #

        existing_user = session.scalar(
            select(UserORM).where(
                UserORM.email == seed_user['email']
            )
        )

        if existing_user is not None:
            print(
                'Usuário de demonstração já existe: '
                f"{seed_user['email']}"
            )
            continue

        now = now_utc()

        #
        # Cria o objeto ORM utilizando o mesmo formato utilizado
        # normalmente pela camada de persistência da aplicação.
        #

        user = UserORM(
            id=uuid_to_bin(seed_user['id']),
            full_name=seed_user['full_name'],
            email=seed_user['email'],
            whatsapp=seed_user['whatsapp'],
            confirmed=seed_user['confirmed'],
            is_admin=seed_user['is_admin'],
            password_hash=password_service.hash_password(seed_user['password']),
            created_at=now,
            updated_at=now
        )

        session.add(user)

        if seed_user['is_admin']:
            print(
                'Usuário administrador criado: '
                f"{seed_user['full_name']} / {seed_user['password']}\n"
            )
        else:
            print(
                'Usuário de demonstração criado: '
                f"{seed_user['full_name']} / {seed_user['password']}"
            )

    #
    # Confirma todas as inserções realizadas pelo processo de seed.
    #

    session.commit()
PYTHON

display_step 'Bootstrap do user-service concluído com sucesso'

exit 0
