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

# UserRepository
from app.repositories.user_repository import UserRepository
from app.repositories.sqlalchemy.sqlalchemy_user_repository import SqlAlchemyUserRepository
from app.repositories.nosql.nosql_user_repository import NosqlUserRepository

# UserPasswordResetTokenRepository
from app.repositories.user_password_reset_token_repository import UserPasswordResetTokenRepository
from app.repositories.sqlalchemy.sqlalchemy_user_password_reset_token_repository import SqlAlchemyUserPasswordResetTokenRepository
from app.repositories.nosql.nosql_user_password_reset_token_repository import NosqlUserPasswordResetTokenRepository

# UserPasswordHistoryRepository
from app.repositories.user_password_history_repository import UserPasswordHistoryRepository
from app.repositories.sqlalchemy.sqlalchemy_user_password_history_repository import SqlAlchemyUserPasswordHistoryRepository
from app.repositories.nosql.nosql_user_password_history_repository import NosqlUserPasswordHistoryRepository

# UserEmailConfirmationTokenRepository
from app.repositories.user_email_confirmation_token_repository import UserEmailConfirmationTokenRepository
from app.repositories.sqlalchemy.sqlalchemy_user_email_confirmation_token_repository import SqlAlchemyUserEmailConfirmationTokenRepository
from app.repositories.nosql.nosql_user_email_confirmation_token_repository import NosqlUserEmailConfirmationTokenRepository

# UserRefreshTokenRepository
from app.repositories.user_refresh_token_repository import UserRefreshTokenRepository
from app.repositories.sqlalchemy.sqlalchemy_user_refresh_token_repository import SqlAlchemyUserRefreshTokenRepository
from app.repositories.nosql.nosql_user_refresh_token_repository import NosqlUserRefreshTokenRepository

# UserAddressRepository
from app.repositories.user_address_repository import UserAddressRepository
from app.repositories.sqlalchemy.sqlalchemy_user_address_repository import SQLAlchemyUserAddressRepository
from app.repositories.nosql.nosql_user_address_repository import NosqlUserAddressRepository


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
    """

    if settings.persistence_provider == 'sqlalchemy':
        return SqlAlchemyUnitOfWork(_require_sqlalchemy_session(session))

    if settings.persistence_provider == 'nosql':
        return NosqlNoOpUnitOfWork()

    raise ValueError(
        f'Unsupported persistence provider: '
        f'{settings.persistence_provider}'
    )


def get_user_repository(
        session: Session | None = Depends(get_session)
) -> UserRepository:
    """
    Monta o repositório de usuários de acordo com o provider
    de persistência configurado.

    Args:
        session: Sessão SQLAlchemy compartilhada pela requisição.

    Returns:
        Repositório de usuários correspondente ao provider configurado.

    Raises:
        RuntimeError: Caso o provider não seja suportado ou a sessão
            SQLAlchemy não esteja disponível.
    """

    if settings.persistence_provider == 'sqlalchemy':
        return SqlAlchemyUserRepository(
            _require_sqlalchemy_session(session)
        )

    if settings.persistence_provider == 'nosql':
        return NosqlUserRepository(handle=get_nosql_handle())

    raise RuntimeError(
        'Unsupported persistence provider: '
        f'{settings.persistence_provider}'
    )


def get_user_email_confirmation_token_repository(
        session: Session | None = Depends(get_session)
) -> UserEmailConfirmationTokenRepository:
    """
    Monta o repositório responsável pela persistência dos tokens
    de confirmação de e-mail.

    Args:
        session: Sessão SQLAlchemy compartilhada pela requisição.

    Returns:
        Repositório de tokens correspondente ao provider configurado.

    Raises:
        RuntimeError: Caso o provider não seja suportado ou a sessão
            SQLAlchemy não esteja disponível.
    """

    if settings.persistence_provider == 'sqlalchemy':
        return SqlAlchemyUserEmailConfirmationTokenRepository(
            _require_sqlalchemy_session(session)
        )

    if settings.persistence_provider == 'nosql':
        return NosqlUserEmailConfirmationTokenRepository(
            handle=get_nosql_handle()
        )

    raise RuntimeError(
        'Unsupported persistence provider: '
        f'{settings.persistence_provider}'
    )


def get_user_password_reset_token_repository(
        session: Session | None = Depends(get_session)
) -> UserPasswordResetTokenRepository:
    """
    Monta o repositório responsável pela persistência dos tokens
    utilizados no processo de redefinição de senha.

    Args:
        session: Sessão SQLAlchemy compartilhada pela requisição.

    Returns:
        Repositório de tokens correspondente ao provider configurado.

    Raises:
        RuntimeError: Caso o provider não seja suportado ou a sessão
            SQLAlchemy não esteja disponível.
    """

    if settings.persistence_provider == 'sqlalchemy':
        return SqlAlchemyUserPasswordResetTokenRepository(
            _require_sqlalchemy_session(session)
        )

    if settings.persistence_provider == 'nosql':
        return NosqlUserPasswordResetTokenRepository(
            handle=get_nosql_handle()
        )

    raise RuntimeError(
        'Unsupported persistence provider: '
        f'{settings.persistence_provider}'
    )


def get_user_password_history_repository(
        session: Session | None = Depends(get_session)
) -> UserPasswordHistoryRepository:
    """
    Monta o repositório responsável pela persistência do histórico
    de senhas dos usuários.

    Args:
        session: Sessão SQLAlchemy compartilhada pela requisição.

    Returns:
        Repositório de histórico correspondente ao provider configurado.

    Raises:
        RuntimeError: Caso o provider não seja suportado ou a sessão
            SQLAlchemy não esteja disponível.
    """

    if settings.persistence_provider == 'sqlalchemy':
        return SqlAlchemyUserPasswordHistoryRepository(
            _require_sqlalchemy_session(session)
        )

    if settings.persistence_provider == 'nosql':
        return NosqlUserPasswordHistoryRepository(
            handle=get_nosql_handle()
        )

    raise RuntimeError(
        'Unsupported persistence provider: '
        f'{settings.persistence_provider}'
    )


def get_user_refresh_token_repository(
        session: Session | None = Depends(get_session)
) -> UserRefreshTokenRepository:
    """
    Monta o repositório responsável pela persistência dos
    refresh tokens associados aos usuários.

    Args:
        session: Sessão SQLAlchemy compartilhada pela requisição.

    Returns:
        Repositório de refresh tokens correspondente ao provider configurado.

    Raises:
        RuntimeError: Caso o provider não seja suportado ou a sessão
            SQLAlchemy não esteja disponível.
    """

    if settings.persistence_provider == 'sqlalchemy':
        return SqlAlchemyUserRefreshTokenRepository(
            _require_sqlalchemy_session(session)
        )

    if settings.persistence_provider == 'nosql':
        return NosqlUserRefreshTokenRepository(
            handle=get_nosql_handle()
        )

    raise RuntimeError(
        'Unsupported persistence provider: '
        f'{settings.persistence_provider}'
    )


def get_user_address_repository(
        session: Session | None = Depends(get_session)
) -> UserAddressRepository:
    """
    Monta o repositório responsável pela persistência dos
    endereços dos usuários.

    Args:
        session: Sessão SQLAlchemy compartilhada pela requisição.

    Returns:
        Repositório de endereços correspondente ao provider configurado.

    Raises:
        RuntimeError: Caso o provider não seja suportado ou a sessão
            SQLAlchemy não esteja disponível.
    """

    if settings.persistence_provider == 'sqlalchemy':
        return SQLAlchemyUserAddressRepository(
            _require_sqlalchemy_session(session)
        )

    if settings.persistence_provider == 'nosql':
        return NosqlUserAddressRepository(handle=get_nosql_handle())

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
