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


async def get_optional_current_user_id(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> UUID:
    pass