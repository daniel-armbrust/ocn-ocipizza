#
# routes/jwks_routes.py
#

import json

from fastapi import APIRouter, Depends

from app.dependencies.security import get_jwt_service
from app.services.jwt_service import JwtService

router = APIRouter()


#
# GET: /.well-known/jwks.json
#
@router.get(
    '/.well-known/jwks.json',
    status_code=200
)
def get_jwks(jwt_service: JwtService = Depends(get_jwt_service)) -> dict:
    """
    Retorna as chaves públicas utilizadas para validação
    dos access tokens JWT emitidos pelo user-service.

    O endpoint segue o formato JWKS e pode ser utilizado pelos
    demais serviços da aplicação para obter as chaves públicas
    necessárias à validação das assinaturas dos JWTs.

    Args:
        jwt_service: Serviço responsável pelas operações
            relacionadas aos access tokens JWT.

    Returns:
        Documento JWKS contendo as chaves públicas disponíveis
        para validação dos tokens.
    """

    return jwt_service.get_jwks()