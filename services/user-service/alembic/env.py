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
