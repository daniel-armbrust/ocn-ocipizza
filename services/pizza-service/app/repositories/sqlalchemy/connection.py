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


def get_session() -> Generator[Session, None, None]:
    """
    Fornece uma sessão SQLAlchemy para acesso ao banco de dados.

    Yields:
        Sessão SQLAlchemy configurada.

    Raises:
        RuntimeError: Caso SQLAlchemy não seja o provider
            de persistência configurado.
    """

    if SessionLocal is None:
        raise RuntimeError(
            'SQLAlchemy is not the configured persistence provider.'
        )

    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()