#
# clients/admin_user_client.py
#

from typing import Any
from uuid import UUID

import httpx

from app.config.settings import settings


class AdminUserClient:
    """
    Cliente HTTP para as operações administrativas do user-service.
    """

    def __init__(self, base_url: str) -> None:
        """
        Inicializa o cliente com a URL-base do user-service.

        Args:
            base_url: URL utilizada como prefixo das requisições.
        """

        self.base_url = base_url.rstrip('/')

    async def get_all(self,
                      access_token: str,
                      email: str | None = None,
                      is_admin: bool | None = None,
                      is_kitchen: bool | None = None,
                      limit: int = 50,
                      offset: int = 0) -> list[dict]:
        """
        Obtém uma página de usuários no user-service.

        Args:
            access_token: Token JWT da sessão administrativa.
            email: Parte do e-mail usada como filtro opcional.
            is_admin: Filtra usuários com acesso administrativo.
            is_kitchen: Filtra usuários com acesso à cozinha.
            limit: Quantidade máxima de usuários retornados.
            offset: Quantidade de usuários ignorados.

        Returns:
            Lista de usuários retornada pelo user-service.

        Raises:
            httpx.HTTPStatusError: Quando o user-service rejeita a consulta.
            httpx.RequestError: Quando ocorre uma falha de comunicação.
        """

        params: dict[str, Any] = {
            'limit': limit,
            'offset': offset
        }

        if email:
            params['email'] = email

        if is_admin is not None:
            params['is_admin'] = is_admin

        if is_kitchen is not None:
            params['is_kitchen'] = is_kitchen

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.get(
                f'{self.base_url}/admin/users',
                params=params,
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

        return response.json()['data']['users']

    async def get_by_id(self,
                        access_token: str,
                        user_id: UUID) -> dict:
        """
        Obtém os dados de um usuário pelo identificador.

        Args:
            access_token: Token JWT da sessão administrativa.
            user_id: Identificador UUID do usuário consultado.

        Returns:
            Dados do usuário retornados pelo user-service.

        Raises:
            httpx.HTTPStatusError: Quando o user-service rejeita a consulta.
            httpx.RequestError: Quando ocorre uma falha de comunicação.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.get(
                f'{self.base_url}/admin/users/{user_id}',
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

        return response.json()['data']['user']

    async def create(self,
                     access_token: str,
                     payload: dict[str, Any]) -> dict:
        """
        Cria um usuário por meio do endpoint administrativo.

        Args:
            access_token: Token JWT da sessão administrativa.
            payload: Dados validados para criação do usuário.

        Returns:
            Usuário criado pelo user-service.

        Raises:
            httpx.HTTPStatusError: Quando o user-service rejeita a criação.
            httpx.RequestError: Quando ocorre uma falha de comunicação.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.post(
                f'{self.base_url}/admin/users',
                json=payload,
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

        return response.json()['data']['user']

    async def update(self,
                     access_token: str,
                     user_id: UUID,
                     payload: dict[str, Any]) -> dict:
        """
        Atualiza os dados administrativos de um usuário.

        Args:
            access_token: Token JWT da sessão administrativa.
            user_id: Identificador UUID do usuário atualizado.
            payload: Dados validados para atualização do usuário.

        Returns:
            Usuário atualizado pelo user-service.

        Raises:
            httpx.HTTPStatusError: Quando o user-service rejeita a alteração.
            httpx.RequestError: Quando ocorre uma falha de comunicação.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.put(
                f'{self.base_url}/admin/users/{user_id}',
                json=payload,
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

        return response.json()['data']['user']

    async def delete(self,
                     access_token: str,
                     user_id: UUID) -> None:
        """
        Remove um usuário pelo endpoint administrativo.

        Args:
            access_token: Token JWT da sessão administrativa.
            user_id: Identificador UUID do usuário removido.

        Raises:
            httpx.HTTPStatusError: Quando o user-service rejeita a remoção.
            httpx.RequestError: Quando ocorre uma falha de comunicação.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.delete(
                f'{self.base_url}/admin/users/{user_id}',
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()


def get_admin_user_client() -> AdminUserClient:
    """
    Fornece o cliente administrativo configurado para o user-service.

    Returns:
        Instância pronta para uso do `AdminUserClient`.
    """

    return AdminUserClient(
        base_url=settings.user_service_url
    )
