#
# dependencies/database.py
#

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config.settings import settings

from app.repositories.sqlalchemy.connection import get_session

from app.repositories.unit_of_work import UnitOfWork
from app.repositories.sqlalchemy.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from app.repositories.nosql.nosql_unit_of_work import NoSqlUnitOfWork

from app.repositories.user_repository import UserRepository
from app.repositories.sqlalchemy.sqlalchemy_user_repository import SqlAlchemyUserRepository
from app.repositories.nosql.nosql_user_repository import NosqlUserRepository

from app.repositories.user_password_reset_token_repository import UserPasswordResetTokenRepository
from app.repositories.sqlalchemy.sqlalchemy_user_password_reset_token_repository import SqlAlchemyUserPasswordResetTokenRepository
from app.repositories.nosql.nosql_user_password_reset_token_repository import NosqlUserPasswordResetTokenRepository

from app.repositories.user_password_history_repository import UserPasswordHistoryRepository
from app.repositories.sqlalchemy.sqlalchemy_user_password_history_repository import SqlAlchemyUserPasswordHistoryRepository
from app.repositories.nosql.nosql_user_password_history_repository import NosqlUserPasswordHistoryRepository

from app.repositories.user_email_confirmation_token_repository import UserEmailConfirmationTokenRepository
from app.repositories.sqlalchemy.sqlalchemy_user_email_confirmation_token_repository import SqlAlchemyUserEmailConfirmationTokenRepository
from app.repositories.nosql.nosql_user_email_confirmation_token_repository import NosqlUserEmailConfirmationTokenRepository

from app.repositories.user_refresh_token_repository import UserRefreshTokenRepository
from app.repositories.sqlalchemy.sqlalchemy_user_refresh_token_repository import SqlAlchemyUserRefreshTokenRepository
from app.repositories.nosql.nosql_user_refresh_token_repository import NosqlUserRefreshTokenRepository

# TODO: yield SqlAlchemyUserRepository(session)


def get_unit_of_work(
        session: Session = Depends(get_session)
) -> UnitOfWork:
    """
    Monta a unidade de trabalho de acordo com o provider de persistência.

    Args:
        session: Sessão SQLAlchemy utilizada quando o provider configurado for relacional.

    Returns:
        Implementação de `UnitOfWork` correspondente ao provider configurado.
    """

    if settings.persistence_provider == 'sqlalchemy':
        return SqlAlchemyUnitOfWork(session)

    if settings.persistence_provider == 'nosql':
        return NoSqlUnitOfWork()

    raise ValueError(
        f'Unsupported persistence provider: '
        f'{settings.persistence_provider}'
    )


def get_user_repository(
        session: Session = Depends(get_session)
) -> UserRepository:
    """
    Monta o repositório de usuários de acordo com o provider
    de persistência configurado.

    Args:
        session: Sessão SQLAlchemy utilizada quando o provider
            configurado for SQLAlchemy.

    Returns:
        Implementação de `UserRepository` correspondente ao provider
        de persistência configurado.
        
    Raises:
        ValueError: Caso o provider de persistência configurado não possua
            uma implementação suportada.
    """

    if settings.persistence_provider == 'sqlalchemy':
        return SqlAlchemyUserRepository(session)

    if settings.persistence_provider == 'nosql':
        return NosqlUserRepository()

    raise ValueError(
        f'Unsupported persistence provider: '
        f'{settings.persistence_provider}'
    )


def get_user_email_confirmation_token_repository(
        session: Session = Depends(get_session)        
) -> UserEmailConfirmationTokenRepository:
    """
    Monta o repositório responsável pela persistência dos tokens
    de confirmação de e-mail.

    Args:
        session: Sessão SQLAlchemy utilizada para acesso ao banco de dados.

    Returns:
        Implementação de `UserEmailConfirmationTokenRepository` utilizada
        pela aplicação.
    
    Raises:
        ValueError: Caso o provider de persistência configurado não possua
            uma implementação suportada.
    """

    if settings.persistence_provider == 'sqlalchemy':
        return SqlAlchemyUserEmailConfirmationTokenRepository(session)

    if settings.persistence_provider == 'nosql':
        return NosqlUserEmailConfirmationTokenRepository()

    raise ValueError(
        f'Unsupported persistence provider: '
        f'{settings.persistence_provider}'
    )


def get_user_password_reset_token_repository(
        session: Session = Depends(get_session)
) -> UserPasswordResetTokenRepository:
    """
    Fornece o repositório responsável pela persistência dos tokens
    utilizados no processo de redefinição de senha.

    Args:
        session: Sessão SQLAlchemy utilizada pelo repositório.

    Returns:
        Implementação do `UserPasswordResetTokenRepository` baseada
        em SQLAlchemy.
    """

    if settings.persistence_provider == 'sqlalchemy':
        return SqlAlchemyUserPasswordResetTokenRepository(session)
    
    if settings.persistence_provider == 'nosql':
        return NosqlUserPasswordResetTokenRepository()

    raise ValueError(
        f'Unsupported persistence provider: '
        f'{settings.persistence_provider}'
    )


def get_user_password_history_repository(
        session: Session = Depends(get_session)
) -> UserPasswordHistoryRepository:
    """
    Fornece o repositório responsável pela persistência do histórico
    de senhas dos usuários.

    Args:
        session: Sessão SQLAlchemy utilizada pelo repositório.

    Returns:
        Implementação do `UserPasswordHistoryRepository` baseada
        em SQLAlchemy.
    """

    if settings.persistence_provider == 'sqlalchemy':
        return SqlAlchemyUserPasswordHistoryRepository(session)
        
    if settings.persistence_provider == 'nosql':
        return NosqlUserPasswordHistoryRepository()

    raise ValueError(
        f'Unsupported persistence provider: '
        f'{settings.persistence_provider}'
    )


def get_user_refresh_token_repository(
        session: Session = Depends(get_session)
) -> UserRefreshTokenRepository:
    """
    Fornece o repositório responsável pela persistência e consulta
    dos refresh tokens associados aos usuários.

    Args:
        session: Sessão SQLAlchemy utilizada pelo repositório.

    Returns:
        Implementação do `UserRefreshTokenRepository` baseada
        em SQLAlchemy.
    """

    if settings.persistence_provider == 'sqlalchemy':
        return SqlAlchemyUserRefreshTokenRepository(session)
            
    if settings.persistence_provider == 'nosql':
        return NosqlUserRefreshTokenRepository()

    raise ValueError(
            f'Unsupported persistence provider: '
            f'{settings.persistence_provider}'
        )