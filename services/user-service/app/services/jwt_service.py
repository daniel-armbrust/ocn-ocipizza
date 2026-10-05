#
# services/jwt_service.py
#

from datetime import timedelta
from uuid import UUID
from pathlib import Path

import jwt

from app.config.settings import settings
from app.utils.utils import now_utc


class JwtService:
    """
    Serviço responsável pela geração e validação dos access tokens JWT.

    Os access tokens são assinados utilizando uma chave privada RSA.
    A validação pode ser realizada utilizando a chave pública
    correspondente.

    Este serviço não possui conhecimento sobre persistência, usuários
    ou refresh tokens.
    """

    KEY_ID = 'user-service-key-1'

    def __init__(self,
                 private_key: str,
                 public_key: str,
                 issuer: str,
                 audience: str,
                 access_token_expiration_minutes: int) -> None:
        """
        Inicializa o serviço responsável pelos access tokens JWT.

        Args:
            private_key: Chave privada RSA utilizada para assinar
                os access tokens.
            public_key: Chave pública RSA utilizada para validar
                os access tokens.
            issuer: Identificador do serviço responsável pela emissão
                dos tokens.
            audience: Identificador dos serviços autorizados a consumir
                os tokens.
            access_token_expiration_minutes: Tempo de validade do
                access token, em minutos.

        Returns:
            None.
        """

        self.private_key = private_key
        self.public_key = public_key
        self.issuer = issuer
        self.audience = audience
        self.access_token_expiration_minutes =access_token_expiration_minutes

    def create_access_token(self, user_id: UUID, is_admin: bool) -> tuple[str, int]:
        """
        Cria um access token JWT para um usuário autenticado.

        Args:
            user_id: Identificador UUID do usuário.
            is_admin: Indica se o usuário possui privilégios
                administrativos.

        Returns:
            Tupla contendo o access token JWT e seu tempo de validade,
            em segundos.
        """

        # TODO: Implementar suporte à rotação de chaves JWT.
        # Cada chave deverá possuir um `kid` próprio, incluído no header do JWT.
        # O endpoint JWKS deverá publicar as chaves públicas atualmente confiáveis
        # e remover imediatamente chaves comprometidas em rotações emergenciais.

        now = now_utc()

        expires_at = now + timedelta(minutes=self.access_token_expiration_minutes)

        # Claims utilizadas para identificar o usuário e controlar
        # a validade e o contexto de utilização do token.
        payload = {
            'sub': str(user_id),
            'is_admin': is_admin,
            'iss': self.issuer,
            'aud': self.audience,
            'iat': now,
            'exp': expires_at
        }

        # O access token é assinado utilizando a chave privada.
        # A chave privada deve permanecer somente no serviço emissor.
        access_token = jwt.encode(
            payload,
            self.private_key,
            algorithm='RS256',
            headers={'kid': self.KEY_ID}
        )

        expires_in = int(
            timedelta(
                minutes=self.access_token_expiration_minutes
            ).total_seconds()
        )

        return access_token, expires_in

    def decode_access_token(self, token: str) -> dict:
        """
        Valida e decodifica um access token JWT.

        A validação verifica a assinatura, o emissor, a audiência
        e o período de validade do token.

        Args:
            token: Access token JWT que será validado.

        Returns:
            Claims contidas no token após sua validação.

        Raises:
            InvalidTokenError: Caso o token seja inválido.
        """

        # A validação utiliza apenas a chave pública.
        # Dessa forma, serviços consumidores não precisam conhecer
        # a chave privada utilizada para assinar os tokens.
        return jwt.decode(
            token,
            self.public_key,
            algorithms=['RS256'],
            issuer=self.issuer,
            audience=self.audience
        )

    def get_jwks(self) -> dict:
        """
        Retorna a chave pública utilizada para validação dos JWTs
        no formato JSON Web Key Set.

        Returns:
            Documento JWKS contendo a chave pública utilizada
            para validação dos access tokens.
        """

        # Converte a chave pública PEM em um objeto RSA e depois
        # em uma representação JWK.
        rsa_algorithm = jwt.get_algorithm_by_name('RS256')
        public_key = rsa_algorithm.prepare_key(self.public_key)
        public_jwk = jwt.algorithms.RSAAlgorithm.to_jwk(
            public_key,
            as_dict=True
        )

        # Adiciona os metadados utilizados pelos consumidores
        # para identificar a finalidade e o algoritmo da chave.
        public_jwk.update(
            {
                'kid': self.KEY_ID,
                'use': 'sig',
                'alg': 'RS256'
            }
        )

        return {
            'keys': [
                public_jwk
            ]
        }


def get_jwt_service() -> JwtService:
    """
    Fornece o serviço responsável pela geração e validação
    dos access tokens JWT.

    As chaves RSA são carregadas a partir dos arquivos configurados
    para o ambiente de execução.

    Returns:
        Instância configurada de `JwtService`.
    """

    # Carrega a chave privada utilizada pelo user-service
    # para assinatura dos access tokens.
    private_key = Path(
        settings.jwt_private_key_path
    ).read_text(
        encoding='utf-8'
    )

    # Carrega a chave pública correspondente, utilizada
    # para validação dos access tokens.
    public_key = Path(
        settings.jwt_public_key_path
    ).read_text(
        encoding='utf-8'
    )

    return JwtService(
        private_key=private_key,
        public_key=public_key,
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        access_token_expiration_minutes=(
            settings.jwt_access_token_expiration_minutes
        )
    )
