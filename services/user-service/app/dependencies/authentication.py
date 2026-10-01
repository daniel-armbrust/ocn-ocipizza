#
# dependencies/authentication.py
#

from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config.settings import settings

from app.repositories.user_repository import UserRepository
from app.dependencies.database import get_user_repository

from app.repositories.user_refresh_token_repository import UserRefreshTokenRepository
from app.dependencies.database import get_user_refresh_token_repository

from app.services.user_service import UserPasswordService, get_user_password_service

from app.services.user_authentication_service import UserAuthenticationService

from app.services.jwt_service import JwtService
from app.dependencies.security import get_jwt_service

from app.services.token_service import TokenService
from app.dependencies.security import get_token_service

from app.repositories.unit_of_work import UnitOfWork
from app.dependencies.database import get_unit_of_work

bearer_scheme = HTTPBearer()


def get_current_user_id(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        jwt_service: JwtService = Depends(get_jwt_service)
) -> UUID:
    """
    Retorna o identificador do usuário autenticado através
    do access token JWT informado na requisição.

    O token é obtido do cabeçalho HTTP Authorization utilizando
    o esquema Bearer. Após sua validação, o identificador do usuário
    é extraído da claim `sub`.

    Args:
        credentials: Credenciais Bearer extraídas do cabeçalho
            Authorization da requisição.
        jwt_service: Serviço responsável pela validação e decodificação
            dos access tokens JWT.

    Returns:
        UUID correspondente ao usuário autenticado.

    Raises:
        HTTPException: Caso o access token seja inválido, expirado
            ou não possua uma claim `sub` válida.
    """

    try:
        # Valida a assinatura, issuer, audience, expiração e demais
        # informações verificadas pelo JwtService.
        payload = jwt_service.decode_access_token(credentials.credentials)

        # A claim `sub` identifica o usuário para o qual
        # o access token foi emitido.
        subject = payload.get('sub')

        if subject is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid access token.'
            )

        # O user-service utiliza UUID como identificador dos usuários.
        return UUID(subject)
    except HTTPException:
        raise
    except (
        jwt.ExpiredSignatureError,
        jwt.InvalidTokenError,
        ValueError
    ) as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired access token.',
        ) from ex


def get_user_authentication_service(
        user_repository: UserRepository = Depends(get_user_repository),
        user_refresh_token_repository: UserRefreshTokenRepository = Depends(
            get_user_refresh_token_repository
        ),
        user_password_service: UserPasswordService = Depends(
            get_user_password_service
        ),
        jwt_service: JwtService = Depends(get_jwt_service),
        token_service: TokenService = Depends(get_token_service),
        unit_of_work: UnitOfWork = Depends(get_unit_of_work),

) -> UserAuthenticationService:
    """
    Fornece o serviço responsável pelos casos de uso relacionados
    à autenticação dos usuários.

    Args:
        user_repository: Repositório utilizado para consultar usuários.
        user_refresh_token_repository: Repositório utilizado para
            persistir e consultar refresh tokens.
        user_password_service: Serviço utilizado para validar
            as senhas dos usuários.
        jwt_service: Serviço responsável pela geração e validação
            dos access tokens JWT.
        token_service: Serviço responsável pela geração e criação
            do hash dos refresh tokens.
        unit_of_work: Unidade de trabalho utilizada para controle
            transacional.

    Returns:
        Instância de `UserAuthenticationService`.
    """

    return UserAuthenticationService(
        user_repository=user_repository,
        user_refresh_token_repository=user_refresh_token_repository,
        user_password_service=user_password_service,
        jwt_service=jwt_service,
        token_service=token_service,
        unit_of_work=unit_of_work,
        refresh_token_expiration_days=settings.refresh_token_expiration_days
    )