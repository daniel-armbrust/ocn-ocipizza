#
# clients/user_client.py
#

import httpx

from app.config.settings import settings


class UserClient:
    """
    Cliente responsável pela comunicação com o user-service.
    """

    def __init__(self, base_url: str) -> None:
        """
        Inicializa o cliente com a URL do user-service.

        Args:
            base_url: URL-base utilizada nas chamadas ao serviço.

        Returns:
            None.
        """

        self.base_url = base_url.rstrip('/')

    async def create(self,
                     full_name: str,
                     email: str,
                     whatsapp: str,
                     password: str) -> dict:
        """
        Cria um novo usuário através do user-service.

        Args:
            full_name: Nome completo do usuário.
            email: Endereço de e-mail do usuário.
            whatsapp: Número de WhatsApp do usuário.
            password: Senha informada pelo usuário.

        Returns:
            Resposta JSON retornada pelo user-service.

        Raises:
            httpx.HTTPStatusError: Caso o user-service retorne
                uma resposta HTTP de erro.
            httpx.RequestError: Caso ocorra uma falha de comunicação
                com o user-service.
        """

        payload = {
            'full_name': full_name,
            'email': email,
            'whatsapp': whatsapp,
            'password': password
        }

        # O cliente assíncrono evita bloquear o event loop enquanto o
        # frontend-service aguarda a resposta do user-service.
        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.post(
                f'{self.base_url}/users',
                json=payload,
                timeout=settings.http_client_timeout
            )

        # Converte respostas HTTP de erro em exceções.
        response.raise_for_status()

        # Retorna integralmente o JSON produzido pelo user-service.
        return response.json()

    async def login(self,
                    email: str,
                    password: str) -> dict:
        """
        Autentica um usuário através do user-service.

        Args:
            email: Endereço de e-mail do usuário.
            password: Senha informada pelo usuário.

        Returns:
            Resposta JSON retornada pelo user-service.

        Raises:
            httpx.HTTPStatusError: Caso o user-service retorne
                uma resposta HTTP de erro.
            httpx.RequestError: Caso ocorra uma falha de comunicação
                com o user-service.
        """

        payload = {
            'email': email,
            'password': password
        }

        # O cliente assíncrono evita bloquear o event loop enquanto o
        # frontend-service aguarda a resposta do user-service.
        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.post(
                f'{self.base_url}/auth/login',
                json=payload
            )

        # Converte respostas HTTP de erro em exceções.
        response.raise_for_status()

        # Retorna integralmente o JSON produzido pelo user-service.
        return response.json()

    async def logout(self,
                     refresh_token: str) -> None:
        """
        Revoga a sessão do usuário através do user-service.

        Args:
            refresh_token: Token utilizado pelo user-service para
                identificar e revogar a sessão correspondente.

        Raises:
            httpx.HTTPStatusError: Caso o user-service retorne uma
                resposta HTTP de erro.
            httpx.RequestError: Caso ocorra uma falha de comunicação
                com o user-service.
        """

        # Encaminha o refresh token ao endpoint responsável pela
        # revogação da sessão no user-service.
        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.post(
                f'{self.base_url}/auth/logout',
                json={
                    'refresh_token': refresh_token
                }
            )

        # Converte respostas HTTP de erro em exceções para que a
        # camada de rota possa decidir como tratar a falha.
        response.raise_for_status()


def get_user_client() -> UserClient:
    """
    Fornece o cliente utilizado para comunicação com o 
    user-service.

    Returns:
        Instância configurada de `UserClient`.
    """

    return UserClient(
        base_url=settings.user_service_url
    )
