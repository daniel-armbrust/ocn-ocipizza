#
# dependencies/authentication.py
#

from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.jwt_service import JwtService
from app.dependencies.security import get_jwt_service

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
            detail='Invalid or expired access token.'
        ) from ex


def get_current_admin_id(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        jwt_service: JwtService = Depends(get_jwt_service)
) -> UUID:
    """
    Retorna o identificador do usuário autenticado quando ele possui
    privilégios administrativos.

    O access token JWT é obtido através do cabeçalho Authorization,
    validado pelo JwtService e sua claim `is_admin` é utilizada para
    verificar se o usuário possui privilégios administrativos.

    Args:
        credentials: Credenciais Bearer extraídas do cabeçalho
            Authorization da requisição.
        jwt_service: Serviço responsável pela validação e decodificação
            dos access tokens JWT.

    Returns:
        UUID correspondente ao usuário administrador autenticado.

    Raises:
        HTTPException: Caso o access token seja inválido, expirado,
            não possua uma claim `sub` válida ou o usuário não possua
            privilégios administrativos.
    """

    try:
        # Valida a assinatura, expiração, issuer e audience do
        # access token recebido na requisição.
        payload = jwt_service.decode_access_token(credentials.credentials)

        # A claim `sub` contém o identificador UUID do usuário
        # para o qual o access token foi emitido.
        subject = payload.get('sub')

        if subject is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid access token.'
            )

        # A claim `is_admin` informa se o usuário autenticado possui
        # privilégios administrativos.
        if payload.get('is_admin') is not True:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Administrative privileges required.'
            )

        # Converte a claim `sub` para o tipo UUID utilizado
        # internamente pela aplicação.
        return UUID(subject)
    except HTTPException:
        raise
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError) as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired access token.'
        ) from ex