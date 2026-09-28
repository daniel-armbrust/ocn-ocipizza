#
# repositories/sqlalchemy/connection.py
#

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

def get_session() -> Generator[Session, None, None]:
    """
    Fornece uma sessão SQLAlchemy para acesso ao banco de dados.

    A sessão é criada no início do uso e encerrada automaticamente
    ao final da operação.
    """

    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()