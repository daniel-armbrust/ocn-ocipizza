#
# dependencies/database.py
#

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config.settings import settings

from app.repositories.sqlalchemy.connection import get_session

from app.repositories.unit_of_work import UnitOfWork

from app.repositories.sqlalchemy.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork

from app.repositories.nosql.nosql_unit_of_work import NosqlNoOpUnitOfWork

from app.repositories.pizza_repository import PizzaRepository

from app.repositories.sqlalchemy.sqlalchemy_pizza_repository import SqlAlchemyPizzaRepository

from app.repositories.nosql.nosql_pizza_repository import NosqlPizzaRepository
from app.repositories.nosql.connection import get_nosql_handle


def get_unit_of_work(
        session: Session | None = Depends(get_session)
) -> UnitOfWork:
    """
    Monta a unidade de trabalho de acordo com o provider
    de persistência.

    Args:
        session: Sessão SQLAlchemy utilizada quando o
            provider configurado for relacional.

    Returns:
        Implementação de `UnitOfWork` correspondente ao provider
            configurado.

    Raises:
        RuntimeError: Caso o provider não seja suportado ou a sessão
            SQLAlchemy não esteja disponível.
    """

    if settings.persistence_provider == 'sqlalchemy':
        return SqlAlchemyUnitOfWork(_require_sqlalchemy_session(session))

    if settings.persistence_provider == 'nosql':
        return NosqlNoOpUnitOfWork()

    raise RuntimeError(
        'Unsupported persistence provider: '
        f'{settings.persistence_provider}'
    )


def get_pizza_repository(
        session: Session | None = Depends(get_session)
) -> PizzaRepository:
    """
    Fornece a implementação do repositório de pizzas de acordo
    com o provider de persistência configurado.

    Args:
        session: Sessão SQLAlchemy compartilhada pela requisição.

    Returns:
        Implementação de `PizzaRepository` correspondente ao provider
            de persistência configurado.

    Raises:
        RuntimeError: Caso o provider não seja suportado ou a sessão
            SQLAlchemy não esteja disponível.
    """

    if settings.persistence_provider == 'sqlalchemy':
        return SqlAlchemyPizzaRepository(
            _require_sqlalchemy_session(session)
        )

    if settings.persistence_provider == 'nosql':
        return NosqlPizzaRepository(handle=get_nosql_handle())

    raise RuntimeError(
        'Unsupported persistence provider: '
        f'{settings.persistence_provider}'
    )


def _require_sqlalchemy_session(session: Session | None) -> Session:
    """
    Valida a sessão compartilhada usada pelas implementações SQLAlchemy.

    Args:
        session: Sessão resolvida para a requisição atual.

    Returns:
        Sessão SQLAlchemy validada.

    Raises:
        RuntimeError: Caso SQLAlchemy esteja configurado, mas nenhuma sessão
            tenha sido disponibilizada.
    """

    if session is None:
        raise RuntimeError(
            'SQLAlchemy session is unavailable for the configured provider.'
        )

    return session
