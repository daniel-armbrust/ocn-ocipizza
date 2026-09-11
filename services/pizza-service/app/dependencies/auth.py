from __future__ import annotations

import os
from typing import Optional

from fastapi import Header, HTTPException, status


def require_admin(authorization: Optional[str] = Header(default=None)) -> None:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "AUTHENTICATION_REQUIRED",
                "message": "Authentication is required",
            },
        )

    scheme, _, token = authorization.partition(" ")
    expected_token = os.getenv("PIZZA_SERVICE_ADMIN_TOKEN", "admin-token")

    if scheme.lower() != "bearer" or token != expected_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ADMIN_PERMISSION_REQUIRED",
                "message": "Admin permission is required",
            },
        )
