#
# dependencies/database.py
#

from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config.settings import settings

from app.repositories.sqlalchemy.connection import get_session

from app.repositories.unit_of_work import UnitOfWork
from app.repositories.sqlalchemy.connection import SessionLocal
from app.repositories.sqlalchemy.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from app.repositories.nosql.nosql_unit_of_work import NoOpUnitOfWork

from app.repositories.pizza_repository import PizzaRepository

from app.repositories.sqlalchemy.sqlalchemy_pizza_repository import SqlAlchemyPizzaRepository

from app.repositories.nosql.nosql_pizza_repository import NosqlPizzaRepository
from app.repositories.nosql.connection import get_nosql_handle


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
        return NoOpUnitOfWork()

    raise ValueError(
        f'Unsupported persistence provider: '
        f'{settings.persistence_provider}'
    )


def get_pizza_repository() -> Generator[PizzaRepository, None, None]:
    """
    Fornece a implementação do repositório de pizzas de acordo
    com o provider de persistência configurado.

    Quando SQLAlchemy é utilizado, a sessão é criada para a
    requisição e fechada automaticamente ao final do processamento.

    Yields:
        Implementação de `PizzaRepository` correspondente ao provider
        de persistência configurado.

    Raises:
        ValueError: Caso o provider de persistência configurado
            não seja suportado.
    """

    if settings.persistence_provider == 'sqlalchemy':
        # Cria uma sessão exclusiva para a requisição atual.
        session = SessionLocal()

        try:
            yield SqlAlchemyPizzaRepository(session)
        finally:
            # Garante o fechamento da sessão mesmo em caso de erro.
            session.close()
        return

    if settings.persistence_provider == 'nosql':
        yield NosqlPizzaRepository(handle=get_nosql_handle())
        return

    raise ValueError(
        f'Unsupported persistence provider: '
        f'{settings.persistence_provider}'
    )