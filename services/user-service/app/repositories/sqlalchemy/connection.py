#
# repositories/sqlalchemy/connection.py
#

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import settings


# Engines SQLAlchemy utilizados para conexões de 
# escrita e leitura.
write_engine = None
read_engine = None

# Fábricas de sessões SQLAlchemy para operações de
# escrita e leitura.
WriteSessionLocal = None
ReadSessionLocal = None


if settings.persistence_provider == 'sqlalchemy':
    if not settings.database_write_url:
        raise ValueError(
            'DATABASE_WRITE_URL is required when '
            'PERSISTENCE_PROVIDER=sqlalchemy.'
        )

    # Cria o Engine para escrita e leituras que exigem 
    # consistência.
    write_engine = create_engine(
        settings.database_write_url,
        pool_pre_ping=True
    )

    # Cria o Engine para leitura, quando configurado.
    if settings.app_env == 'production':
        read_engine = create_engine(
            settings.database_read_url,
            pool_pre_ping=True
        )
    else:
        read_engine = write_engine

    # Configura as fábricas de sessões SQLAlchemy.
    WriteSessionLocal = sessionmaker(
        bind=write_engine,
        autoflush=False,
        autocommit=False
    )

    ReadSessionLocal = sessionmaker(
        bind=read_engine,
        autoflush=False,
        autocommit=False
    )


def get_session() -> Generator[Session | None, None, None]:
    """
    Fornece uma sessão SQLAlchemy conectada ao banco primário.

    Yields:
        Session | None: Sessão para escrita e leituras consistentes,
        ou None quando o provider não for SQLAlchemy.
    """

    if WriteSessionLocal is None:
        yield None
        return

    session = WriteSessionLocal()

    try:
        yield session
    finally:
        session.close()


def get_read_session() -> Generator[Session | None, None, None]:
    """
    Fornece uma sessão SQLAlchemy para operações de leitura.

    Quando DATABASE_READ_URL não estiver configurada, utiliza
    o mesmo Engine do banco primário.

    Yields:
        Session | None: Sessão para leituras que toleram consistência
        eventual, ou None quando o provider não for SQLAlchemy.
    """

    if ReadSessionLocal is None:
        yield None
        return

    session = ReadSessionLocal()

    try:
        yield session
    finally:
        session.close()