#
# repositories/sqlalchemy/connection.py
#

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import settings


engine = None
SessionLocal = None

if settings.persistence_provider == 'sqlalchemy':
    if not settings.database_url:
        raise ValueError(
            'DATABASE_URL is required when '
            'PERSISTENCE_PROVIDER=sqlalchemy.'
        )

    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True
    )

    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False
    )


def get_session() -> Generator[Session | None, None, None]:
    """
    Fornece uma sessão SQLAlchemy para acesso ao banco de dados.

    Yields:
        Sessão SQLAlchemy configurada quando o provider for relacional.
        Para providers não relacionais, retorna None.
    """

    if SessionLocal is None:
        yield None
        return

    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
