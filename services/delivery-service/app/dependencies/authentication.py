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

    token = credentials.credentials

    try:
        # Obtém apenas o cabeçalho do JWT para identificar a chave pública
        # utilizada na assinatura do token.
        header = jwt.get_unverified_header(token)
        kid = header['kid']

        # Obtém a chave pública do cache ou atualiza o JWKS quando necessário.
        jwk = await jwks_client.get_key(kid)

        public_key = jwt.PyJWK.from_dict(jwk).key

        # Valida criptograficamente o token e também os claims esperados
        # pelo delivery-service.
        payload = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience
        )

        return UUID(payload['sub'])

    except (jwt.InvalidTokenError, KeyError, ValueError):
        # Tokens expirados também geram InvalidTokenError e representam uma
        # falha de autenticação, não um erro interno da aplicação.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired authentication token.'
        )


async def get_current_admin_id(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> UUID:
    """
    Valida o token JWT e retorna o identificador do administrador autenticado.

    Args:
        credentials: Credenciais Bearer extraídas do cabeçalho Authorization.

    Returns:
        Identificador do administrador autenticado.

    Raises:
        HTTPException: Quando o token é inválido ou o usuário autenticado
            não possui privilégio administrativo.
    """

    token = credentials.credentials

    try:
        # Obtém o cabeçalho do JWT sem validar a assinatura para
        # identificar qual chave pública deve ser utilizada.
        header = jwt.get_unverified_header(token)
        kid = header['kid']

        # Obtém a chave pública do cache ou atualiza o JWKS
        # quando a chave ainda não estiver disponível localmente.
        jwk = await jwks_client.get_key(kid)
        public_key = jwt.PyJWK.from_dict(jwk).key

        # Valida a assinatura do JWT e os claims esperados
        # pelo delivery-service.
        payload = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience
        )

        # O user-service emite as permissões administrativas nas claims
        # booleanas `is_admin` e `is_kitchen`; não existe uma claim `role`.
        # As rotas administrativas do delivery-service exigem `is_admin`.
        if payload.get('is_admin') is not True:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Administrator access required.'
            )

        # O claim sub contém o identificador do usuário autenticado.
        return UUID(payload['sub'])

    except HTTPException:
        raise

    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication token.'
        )
