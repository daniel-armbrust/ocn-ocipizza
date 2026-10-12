#
# dependencies/database.py
#

from borneo import NoSQLHandle
from fastapi import Depends
from sqlalchemy.orm import Session

from app.config.settings import settings

from app.repositories.sqlalchemy.connection import get_session
from app.repositories.nosql.connection import get_nosql_handle

from app.repositories.unit_of_work import UnitOfWork
from app.repositories.sqlalchemy.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from app.repositories.nosql.nosql_unit_of_work import NosqlNoOpUnitOfWork

from app.repositories.pizza_repository import PizzaRepository
from app.repositories.nosql.nosql_pizza_repository import NosqlPizzaRepository


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
    session: Session | None = Depends(get_session),
    handle: NoSQLHandle | None = Depends(get_nosql_handle)
) -> PizzaRepository:
    """
    Fornece o repositório correspondente ao provider configurado.

    Args:
        session: Sessão disponibilizada quando o provider for relacional.
        handle: Handle Oracle NoSQL compartilhado pela requisição.

    Returns:
        Repositório de pizzas configurado para a requisição atual.

    Raises:
        RuntimeError: Quando o provider não for suportado ou ainda não possuir
            uma implementação de repositório.
    """

    if settings.persistence_provider == 'nosql':
        return NosqlPizzaRepository(
            handle=_require_nosql_handle(handle),
            table_name=settings.nosql_table_name
        )

    if settings.persistence_provider == 'sqlalchemy':
        _require_sqlalchemy_session(session)
        raise RuntimeError(
            'SQLAlchemy pizza repository is not implemented.'
        )

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


def _require_nosql_handle(handle: NoSQLHandle | None) -> NoSQLHandle:
    """
    Valida o handle compartilhado usado pelas implementações Oracle NoSQL.

    Args:
        handle: Handle resolvido para a requisição atual.

    Returns:
        Handle Oracle NoSQL validado.

    Raises:
        RuntimeError: Caso NoSQL esteja configurado, mas nenhum handle
            tenha sido disponibilizado.
    """

    if handle is None:
        raise RuntimeError(
            'Oracle NoSQL handle is unavailable for the configured provider.'
        )

    return handle
