#
# dependencies/database.py
#

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config.settings import settings

from app.repositories.sqlalchemy.connection import get_session
from app.repositories.nosql.connection import get_nosql_handle

from app.repositories.unit_of_work import UnitOfWork
from app.repositories.sqlalchemy.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from app.repositories.nosql.nosql_unit_of_work import NosqlNoOpUnitOfWork

from app.repositories.delivery_area_repository import DeliveryAreaRepository
from app.repositories.sqlalchemy.sqlalchemy_delivery_area_repository import SqlAlchemyDeliveryAreaRepository
from app.repositories.nosql.nosql_delivery_area_repository import NosqlDeliveryAreaRepository


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


def get_delivery_area_repository(
        session: Session | None = Depends(get_session)
) -> DeliveryAreaRepository:
    """ Obtém o repositório responsável pela persistência das 
    áreas de entrega. 
    
    Args: 
        session: Sessão utilizada para acesso à camada de persistência. 
    
    Returns: 
        Repositório responsável pelas operações de persistência das 
            áreas de entrega. 
    """
    
    if settings.persistence_provider == 'sqlalchemy':
        return SqlAlchemyDeliveryAreaRepository(
            _require_sqlalchemy_session(session)
        )

    if settings.persistence_provider == 'nosql':
        return NosqlDeliveryAreaRepository(handle=get_nosql_handle())
    
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