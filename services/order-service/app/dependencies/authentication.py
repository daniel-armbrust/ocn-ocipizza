#
# dependencies/authentication.py
#

from uuid import UUID

import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config.settings import settings

from app.clients.jwks_client import jwks_client

bearer_scheme = HTTPBearer()


async def get_current_user_id(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> UUID:
    """
    Valida o token JWT e retorna o identificador do usuário autenticado.

    Args:
        credentials: Credenciais Bearer extraídas do cabeçalho Authorization.

    Returns:
        Identificador do usuário autenticado.

    Raises:
        HTTPException: Quando o token está expirado, é inválido ou não contém
            os dados necessários para identificar o usuário.
    """

    # Centraliza a validação criptográfica e dos claims comuns do token.
    payload = await _get_authenticated_payload(credentials)

    return UUID(payload['sub'])


async def get_current_admin_id(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> UUID:
    """
    Valida o token JWT e retorna o identificador do administrador de pedidos.

    Somente administradores da aplicação podem utilizar esta dependência.

    Args:
        credentials: Credenciais Bearer extraídas do cabeçalho Authorization.

    Returns:
        Identificador do administrador de pedidos autenticado.

    Raises:
        HTTPException: Quando o token é inválido ou o usuário autenticado
            não possui acesso administrativo aos pedidos.
    """

    # Valida o token antes de verificar a permissão exclusiva de administrador.
    payload = await _get_authenticated_payload(credentials)

    # Impede que usuários da cozinha utilizem operações exclusivas de admin.
    if payload.get('is_admin') is not True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Administrator access required.'
        )

    return UUID(payload['sub'])


async def get_current_kitchen_id(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> UUID:
    """Valida que o token pertença a um usuário da cozinha."""

    # Valida o token antes de verificar a permissão específica da cozinha.
    payload = await _get_authenticated_payload(credentials)

    # Garante que somente usuários marcados como cozinha acessem esta função.
    if payload.get('is_kitchen') is not True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Kitchen access required.'
        )

    return UUID(payload['sub'])


async def get_current_order_operator_id(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> UUID:
    """
    Valida usuários autorizados a operar o fluxo de pedidos.

    Administradores e usuários da cozinha podem consultar e atualizar pedidos,
    mas operações exclusivas, como exclusão, usam dependências específicas.
    """

    # Valida o token antes de verificar o perfil operacional do usuário.
    payload = await _get_authenticated_payload(credentials)

    # Permite a operação compartilhada apenas para admin ou cozinha.
    if (
        payload.get('is_admin') is not True
        and payload.get('is_kitchen') is not True
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Order operator access required.'
        )

    return UUID(payload['sub'])


async def _get_authenticated_payload(
        credentials: HTTPAuthorizationCredentials
) -> dict:
    """Valida o token e retorna seus claims autenticados."""

    token = credentials.credentials

    try:
        # Obtém apenas o cabeçalho do JWT para identificar a chave pública
        # utilizada na assinatura do token.
        header = jwt.get_unverified_header(token)
        kid = header['kid']

        # Obtém a chave pública do cache ou atualiza o JWKS quando necessário.
        jwk = await jwks_client.get_key(kid)
        public_key = jwt.PyJWK.from_dict(jwk).key

        return jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience
        )

    except (jwt.InvalidTokenError, KeyError, ValueError):
        # Tokens expirados também geram InvalidTokenError e representam uma
        # falha de autenticação, não um erro interno da aplicação.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired authentication token.'
        )
