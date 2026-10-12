#
# services/user_auth_service.py
#

from fastapi import Depends

from app.clients.user_auth_client import UserAuthClient, get_user_auth_client


class UserAuthService:
    """
    Coordena os casos de uso de autenticação junto ao user-service.

    O serviço interpreta o contrato da API de autenticação sem conhecer
    cookies, templates, redirects ou a implementação das sessões do BFF.
    """

    def __init__(self, user_auth_client: UserAuthClient) -> None:
        """
        Inicializa o serviço com o cliente do user-service.

        Args:
            user_auth_client: Cliente utilizado para autenticar e revogar
                sessões no user-service.

        Returns:
            None.
        """

        self.user_auth_client = user_auth_client

    async def authenticate(self, email: str, password: str) -> dict:
        """
        Autentica um usuário e retorna os dados necessários para a sessão.

        Args:
            email: Endereço de e-mail informado pelo usuário.
            password: Senha informada pelo usuário.

        Returns:
            Tokens e prazo de expiração retornados pelo user-service.

        Raises:
            httpx.HTTPStatusError: Caso o user-service rejeite a
                autenticação.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                user-service.
            KeyError: Caso a resposta não contenha os dados de autenticação
                esperados.
        """

        payload = await self.user_auth_client.login(
            email=email,
            password=password
        )

        # O user-service encapsula tokens e expiração no campo `data` da
        # resposta JSend. A rota recebe somente os dados necessários à sessão.
        return payload['data']

    async def logout(self, refresh_token: str) -> None:
        """
        Solicita a revogação da sessão no user-service.

        Args:
            refresh_token: Token que identifica a sessão que será revogada.

        Returns:
            None.

        Raises:
            httpx.HTTPStatusError: Caso o user-service rejeite a revogação.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                user-service.
        """

        await self.user_auth_client.logout(refresh_token=refresh_token)


def get_user_auth_service(
    user_auth_client: UserAuthClient = Depends(get_user_auth_client)
) -> UserAuthService:
    """
    Fornece o serviço responsável pelos casos de uso de autenticação.

    Args:
        user_auth_client: Cliente configurado para acessar o user-service.

    Returns:
        Instância configurada de `UserAuthService`.
    """

    return UserAuthService(user_auth_client=user_auth_client)
