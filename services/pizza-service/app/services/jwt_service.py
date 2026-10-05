#
# services/jwt_services.py
#

import jwt

from app.config.settings import settings


class JwtService:
    """
    Serviço responsável pela validação dos JWTs emitidos
    pelo user-service.
    """

    def __init__(self) -> None:
        """
        Inicializa o cliente utilizado para obtenção das chaves
        públicas publicadas pelo user-service.
        """

        self.jwks_client = jwt.PyJWKClient(settings.jwt_jwks_url)

    def decode_access_token(self, token: str) -> dict:
        """
        Valida e decodifica um access token.

        Args:
            token: JWT recebido na requisição.

        Returns:
            Claims contidas no JWT validado.

        Raises:
            jwt.InvalidTokenError: Caso o token seja inválido,
                expirado ou não possa ser validado.
        """

        # Obtém a chave pública correspondente ao `kid` presente 
        # no header do JWT.
        signing_key = self.jwks_client.get_signing_key_from_jwt(token)

        return jwt.decode(
            token,
            signing_key.key,
            algorithms=['RS256'],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience
        )


def get_jwt_service() -> JwtService:
    """
    Fornece o serviço responsável pela validação de JWTs.
    """

    return JwtService()