#
# clients/user_client.py
#

from uuid import UUID

import httpx

from app.config.settings import settings


class UserClient:
    """
    Cliente responsável pelas operações de cadastro, consulta e
    gerenciamento dos dados dos usuários junto ao user-service.
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

    async def update_whatsapp(self,
                              access_token: str,
                              whatsapp: str) -> dict:
        """
        Atualiza o número de WhatsApp do usuário autenticado.

        Args:
            access_token: Token de acesso JWT do usuário autenticado.
            whatsapp: Novo número de WhatsApp do usuário.

        Returns:
            JSON retornado pelo user-service após a atualização.
        """

        payload = {
            'whatsapp': whatsapp
        }

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        # O cliente assíncrono evita bloquear o event loop enquanto o
        # frontend-service aguarda a resposta do user-service.
        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.put(
                f'{self.base_url}/users/me',
                json=payload,
                headers=headers,
                timeout=settings.http_client_timeout
            )

        # Converte respostas HTTP de erro em exceções.
        response.raise_for_status()

        # Retorna integralmente o JSON produzido pelo user-service.
        return response.json()

    async def get_profile(self, access_token: str) -> dict:
        """
        Obtém os dados do perfil do usuário autenticado.

        Args:
            access_token: Token de acesso JWT do usuário autenticado.

        Returns:
            Dados do perfil do usuário retornados pelo user-service.

        Raises:
            httpx.HTTPStatusError: Caso o user-service retorne uma resposta
                HTTP de erro.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                user-service.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        # O cliente assíncrono evita bloquear o event loop enquanto o
        # frontend-service aguarda a resposta do user-service.
        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.get(
                f'{self.base_url}/users/me',
                headers=headers,
                timeout=settings.http_client_timeout
            )

        # Converte respostas HTTP de erro em exceções.
        response.raise_for_status()

        # Obtém a resposta JSend produzida pelo user-service.
        data = response.json()

        # Retorna somente os dados do usuário para simplificar o uso
        # pelas rotas e templates do frontend-service.
        return data['data']['user']

    async def get_addresses(self, access_token: str) -> list[dict]:
        """
        Obtém os endereços do usuário autenticado.

        Args:
            access_token: Token de acesso JWT do usuário autenticado.

        Returns:
            Endereços retornados pelo user-service.

        Raises:
            httpx.HTTPStatusError: Caso o user-service retorne uma resposta
                HTTP de erro.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                user-service.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.get(
                f'{self.base_url}/users/me/addresses',
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

        return response.json()['data']['addresses']

    async def create_address(self,
                             access_token: str,
                             label: str | None,
                             zip_code: str,
                             street: str,
                             number: str,
                             complement: str | None,
                             neighborhood: str,
                             city: str,
                             state: str,
                             is_default: bool) -> dict:
        """
        Cadastra um endereço para o usuário autenticado.

        Args:
            access_token: Token de acesso JWT do usuário autenticado.
            label: Identificação opcional do endereço.
            zip_code: CEP do endereço.
            street: Logradouro do endereço.
            number: Número do endereço.
            complement: Complemento opcional do endereço.
            neighborhood: Bairro do endereço.
            city: Cidade do endereço.
            state: Sigla do estado.
            is_default: Indica se o endereço será o principal.

        Returns:
            Endereço cadastrado retornado pelo user-service.

        Raises:
            httpx.HTTPStatusError: Caso o user-service retorne uma resposta
                HTTP de erro.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                user-service.
        """

        payload = {
            'label': label,
            'zip_code': zip_code,
            'street': street,
            'number': number,
            'complement': complement,
            'neighborhood': neighborhood,
            'city': city,
            'state': state,
            'is_default': is_default
        }

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.post(
                f'{self.base_url}/users/me/addresses',
                json=payload,
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

        return response.json()['data']['address']

    async def delete_address(self,
                             access_token: str,
                             address_id: UUID) -> None:
        """
        Remove um endereço do usuário autenticado.

        Args:
            access_token: Token de acesso JWT do usuário autenticado.
            address_id: Identificador único do endereço removido.

        Returns:
            None.

        Raises:
            httpx.HTTPStatusError: Caso o user-service retorne uma resposta
                HTTP de erro.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                user-service.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.delete(
                f'{self.base_url}/users/me/addresses/{address_id}',
                headers=headers,
                timeout=settings.http_client_timeout
            )

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
