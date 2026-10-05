#
# dependencies/authentication.py
#

from uuid import UUID

import jwt
from jwt.exceptions import PyJWKClientConnectionError, PyJWKClientError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.jwt_service import JwtService, get_jwt_service

security = HTTPBearer(auto_error=False)


def get_current_admin_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    jwt_service: JwtService = Depends(get_jwt_service)
) -> UUID:
    """
    Valida o JWT e retorna o identificador do usuário administrador.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication credentials were not provided.',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    try:
        payload = jwt_service.decode_access_token(
            credentials.credentials
        )

        user_id = UUID(payload['sub'])
    except PyJWKClientConnectionError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Token validation service is unavailable.'
        ) from exc
    except (
        jwt.InvalidTokenError,
        PyJWKClientError,
        KeyError,
        ValueError
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired access token.',
            headers={'WWW-Authenticate': 'Bearer'}
        ) from exc

    if payload.get('is_admin') is not True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Administrator privileges required.',
        )

    return user_id
