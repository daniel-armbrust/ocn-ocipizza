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

from app.repositories.password_reset_token_repository import PasswordResetTokenRepository
from app.repositories.sqlalchemy.sqlalchemy_password_reset_token_repository import SqlAlchemyPasswordResetTokenRepository

from app.repositories.password_history_repository import PasswordHistoryRepository
from app.repositories.sqlalchemy.sqlalchemy_password_history_repository import SqlAlchemyPasswordHistoryRepository

from app.repositories.email_confirmation_token_repository import EmailConfirmationTokenRepository
from app.repositories.sqlalchemy.sqlalchemy_email_confirmation_token_repository import SqlAlchemyEmailConfirmationTokenRepository
from app.repositories.nosql.nosql_email_confirmation_token_repository import NosqlEmailConfirmationTokenRepository


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


def get_email_confirmation_token_repository(
        session: Session = Depends(get_session)        
) -> EmailConfirmationTokenRepository:
    """
    Monta o repositório responsável pela persistência dos tokens
    de confirmação de e-mail.

    Args:
        session: Sessão SQLAlchemy utilizada para acesso ao banco de dados.

    Returns:
        Implementação de `EmailConfirmationTokenRepository` utilizada
        pela aplicação.
    
    Raises:
        ValueError: Caso o provider de persistência configurado não possua
            uma implementação suportada.
    """

    if settings.persistence_provider == 'sqlalchemy':
        return SqlAlchemyEmailConfirmationTokenRepository(session)

    if settings.persistence_provider == 'nosql':
        return NosqlEmailConfirmationTokenRepository()

    raise ValueError(
        f'Unsupported persistence provider: '
        f'{settings.persistence_provider}'
    )


def get_password_reset_token_repository(
    session: Session = Depends(get_session),
) -> PasswordResetTokenRepository:
    """
    Fornece o repositório responsável pela persistência dos tokens
    utilizados no processo de redefinição de senha.

    Args:
        session: Sessão SQLAlchemy utilizada pelo repositório.

    Returns:
        Implementação do `PasswordResetTokenRepository` baseada
        em SQLAlchemy.
    """

    return SqlAlchemyPasswordResetTokenRepository(
        session=session,
    )


def get_password_history_repository(
    session: Session = Depends(get_session),
) -> PasswordHistoryRepository:
    """
    Fornece o repositório responsável pela persistência do histórico
    de senhas dos usuários.

    Args:
        session: Sessão SQLAlchemy utilizada pelo repositório.

    Returns:
        Implementação do `PasswordHistoryRepository` baseada
        em SQLAlchemy.
    """

    return SqlAlchemyPasswordHistoryRepository(
        session=session,
    )