#
# services/admin_auth_service.py
#

import jwt
from uuid import UUID

from fastapi import Depends

from app.clients.user_auth_client import (
    UserAuthClient,
    get_user_auth_client
)

from app.config.settings import settings

from app.exceptions.admin_auth_exceptions import (
    AdminAccessDeniedError,
    AdminAuthenticationError
)

from app.clients.jwks_client import jwks_client


class AdminAuthService:
    """
    Implementa as regras de autenticação e autorização
    utilizadas pelo painel administrativo.
    """

    def __init__(self, user_auth_client: UserAuthClient):
        """
        Inicializa o serviço responsável pela autenticação administrativa.

        Args:
            user_auth_client: Cliente responsável pela comunicação
                com o user-service.
        """

        self.user_auth_client = user_auth_client

    async def login(self, email: str, password: str) -> dict:
        """
        Autentica um usuário e valida seu acesso ao painel administrativo.

        Args:
            email: Endereço de e-mail utilizado para autenticação.
            password: Senha utilizada para autenticação.

        Returns:
            Dados necessários para criação da sessão administrativa.

        Raises:
            AdminAuthenticationError: Quando não é possível autenticar
                ou validar criptograficamente o usuário.
            AdminAccessDeniedError: Quando o usuário autenticado não possui
                um perfil autorizado para acessar o painel.
        """

        try:
            # Delega ao user-service a validação das credenciais
            # e a geração dos tokens utilizados pela aplicação.
            response = await self.user_auth_client.login(
                email=email,
                password=password
            )
        except Exception as ex:
            raise AdminAuthenticationError(
                'Unable to authenticate administrative user.'
            ) from ex

        try:
            # O user-service utiliza o padrão JSend e encapsula os dados
            # de autenticação no atributo `data` da resposta.
            authentication = response['data']
        except (KeyError, TypeError) as ex:
            raise AdminAuthenticationError(
                'Invalid authentication response returned by user-service.'
            ) from ex

        access_token = authentication.get('access_token')
        refresh_token = authentication.get('refresh_token')
        expires_in = authentication.get('expires_in')

        if not access_token or not refresh_token or not expires_in:
            raise AdminAuthenticationError(
                'Required authentication data was not returned by user-service.'
            )

        try:
            # Obtém o cabeçalho do JWT sem validar a assinatura para
            # identificar qual chave pública deve ser utilizada.
            header = jwt.get_unverified_header(access_token)

            kid = header['kid']

            # Obtém a chave pública correspondente ao kid utilizando
            # o cache local ou o endpoint JWKS do user-service.
            jwk = await jwks_client.get_key(kid)

            public_key = jwt.PyJWK.from_dict(jwk).key

            # Valida criptograficamente o JWT e também os claims
            # obrigatórios esperados pelo admin-service.
            payload = jwt.decode(
                access_token,
                public_key,
                algorithms=['RS256'],
                issuer=settings.jwt_issuer,
                audience=settings.jwt_audience
            )
        except (
            jwt.InvalidTokenError,
            KeyError,
            ValueError
        ) as ex:
            raise AdminAuthenticationError(
                'Invalid access token returned by user-service.'
            ) from ex

        user_id = payload.get('sub')
        is_admin = payload.get('is_admin')
        is_kitchen = payload.get('is_kitchen')

        if (
            not user_id
            or not isinstance(is_admin, bool)
            or not isinstance(is_kitchen, bool)
        ):
            raise AdminAuthenticationError(
                'Required claims were not returned in access token.'
            )

        # Somente administradores e usuários da cozinha podem
        # acessar as funcionalidades disponibilizadas pelo admin-service.
        if not is_admin and not is_kitchen:
            raise AdminAccessDeniedError(
                'User is not authorized to access admin-service.'
            )

        # Valida também o formato do identificador recebido no claim sub.
        try:
            user_id = str(UUID(user_id))
        except ValueError as ex:
            raise AdminAuthenticationError(
                'Invalid user identifier returned in access token.'
            ) from ex

        # Retorna somente os dados necessários para criação
        # da sessão administrativa no Redis.
        return {
            'user_id': user_id,
            'is_admin': is_admin,
            'is_kitchen': is_kitchen,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': expires_in
        }

    async def logout(self, refresh_token: str) -> None:
        """
        Solicita a revogação da sessão no user-service.

        Args:
            refresh_token: Token utilizado para identificar a sessão que será
                revogada pelo user-service.

        Returns:
            None.

        Raises:
            httpx.HTTPStatusError: Quando o user-service rejeita a operação.
            httpx.RequestError: Quando ocorre uma falha de comunicação com o
                user-service.
        """

        await self.user_auth_client.logout(
            refresh_token=refresh_token
        )


def get_admin_auth_service(
        user_auth_client: UserAuthClient = Depends(
            get_user_auth_client
        )
) -> AdminAuthService:
    """
    Retorna o serviço responsável pela autenticação dos usuários
    autorizados a acessar o admin-service.

    Args:
        user_auth_client: Cliente responsável pela comunicação
            com o user-service.

    Returns:
        Serviço responsável pela autenticação administrativa.
    """
    return AdminAuthService(
        user_auth_client=user_auth_client
    )
