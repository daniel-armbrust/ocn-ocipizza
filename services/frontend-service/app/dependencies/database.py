#
# dependencies/database.py
#

from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config.settings import settings

from app.repositories.sqlalchemy.connection import get_session

from app.repositories.unit_of_work import UnitOfWork

from app.repositories.session_repository import SessionRepository

from app.repositories.sqlalchemy.connection import SessionLocal
from app.repositories.sqlalchemy.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from app.repositories.sqlalchemy.sqlalchemy_session_repository import SqlAlchemySessionRepository

from app.repositories.redis.connection import get_redis_client
from app.repositories.redis.redis_session_repository import RedisSessionRepository
from app.repositories.redis.redis_unit_of_work import RedisNoOpUnitOfWork

from app.repositories.nosql.connection import get_nosql_handle
from app.repositories.nosql.nosql_session_repository import NosqlSessionRepository
from app.repositories.nosql.nosql_unit_of_work import NosqlNoOpUnitOfWork


def get_unit_of_work() -> UnitOfWork:
    """
    Monta a unidade de trabalho de acordo com o provider 
    de persistência.

    Args:
        session: Sessão SQLAlchemy utilizada quando o 
            provider configurado for relacional.

    Returns:
        Implementação de `UnitOfWork` correspondente ao provider 
            configurado.
    """

    if settings.persistence_provider == 'sqlalchemy':
        session = next(get_session())

        return SqlAlchemyUnitOfWork(session)

    if settings.persistence_provider == 'nosql':
        return NosqlNoOpUnitOfWork()

    if settings.persistence_provider == 'redis':
        return RedisNoOpUnitOfWork()

    raise ValueError(
        f'Unsupported persistence provider: '
        f'{settings.persistence_provider}'
    )


def get_session_repository() -> Generator[SessionRepository, None, None]:
    """
    Retorna a implementação do repositório de sessões de acordo
    com o provedor de persistência configurado.
    """

    if settings.persistence_provider == 'sqlalchemy':
        # Cria uma sessão exclusiva para a requisição atual.
        session = SessionLocal()

        try:
            yield SqlAlchemySessionRepository(session)
        finally:
            # Garante o fechamento da sessão mesmo em caso de erro.
            session.close()
        return

    if settings.persistence_provider == 'nosql':
        yield NosqlSessionRepository(handle=get_nosql_handle())
        return

    if settings.persistence_provider == 'redis':
        yield RedisSessionRepository(client=get_redis_client())
        return

    raise RuntimeError(
        'Unsupported persistence provider: '
        f'{settings.persistence_provider}'
    )