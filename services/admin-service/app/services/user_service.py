#
# services/user_service.py
#

from typing import Any
from uuid import UUID

from fastapi import Depends

from app.clients.admin_user_client import (
    AdminUserClient,
    get_admin_user_client
)


class UserService:
    """
    Coordena as operações administrativas relacionadas aos usuários.

    A autorização permanece nas dependências das rotas. Esta camada apenas
    organiza os casos de uso e delega a comunicação ao cliente HTTP.
    """

    def __init__(self, admin_user_client: AdminUserClient) -> None:
        """
        Inicializa o serviço com o cliente administrativo de usuários.

        Args:
            admin_user_client: Cliente HTTP utilizado para acessar o
                user-service.
        """

        self.admin_user_client = admin_user_client

    async def get_all(self,
                      access_token: str,
                      email: str | None = None,
                      is_admin: bool | None = None,
                      is_kitchen: bool | None = None,
                      limit: int = 50,
                      offset: int = 0) -> list[dict]:
        """
        Obtém uma página de usuários para o painel administrativo.

        Args:
            access_token: Token JWT da sessão administrativa.
            email: Parte do e-mail usada como filtro opcional.
            is_admin: Filtra usuários administradores.
            is_kitchen: Filtra usuários da cozinha.
            limit: Quantidade máxima de usuários retornados.
            offset: Quantidade de usuários ignorados.

        Returns:
            Lista de usuários retornada pelo user-service.

        Raises:
            httpx.HTTPStatusError: Quando o user-service rejeita a consulta.
            httpx.RequestError: Quando ocorre uma falha de comunicação.
        """

        return await self.admin_user_client.get_all(
            access_token=access_token,
            email=email,
            is_admin=is_admin,
            is_kitchen=is_kitchen,
            limit=limit,
            offset=offset
        )

    async def get_by_id(self,
                        access_token: str,
                        user_id: UUID) -> dict:
        """
        Obtém os dados de um usuário específico.

        Args:
            access_token: Token JWT da sessão administrativa.
            user_id: Identificador UUID do usuário consultado.

        Returns:
            Dados do usuário retornados pelo user-service.

        Raises:
            httpx.HTTPStatusError: Quando o user-service rejeita a consulta.
            httpx.RequestError: Quando ocorre uma falha de comunicação.
        """

        return await self.admin_user_client.get_by_id(
            access_token=access_token,
            user_id=user_id
        )

    async def create(self,
                     access_token: str,
                     payload: dict[str, Any]) -> dict:
        """
        Cria um usuário no user-service.

        Args:
            access_token: Token JWT da sessão administrativa.
            payload: Dados validados para criação do usuário.

        Returns:
            Usuário criado pelo user-service.

        Raises:
            httpx.HTTPStatusError: Quando o user-service rejeita a criação.
            httpx.RequestError: Quando ocorre uma falha de comunicação.
        """

        return await self.admin_user_client.create(
            access_token=access_token,
            payload=payload
        )

    async def update(self,
                     access_token: str,
                     user_id: UUID,
                     payload: dict[str, Any]) -> dict:
        """
        Atualiza os dados administrativos de um usuário.

        Args:
            access_token: Token JWT da sessão administrativa.
            user_id: Identificador UUID do usuário atualizado.
            payload: Dados validados para atualização.

        Returns:
            Usuário atualizado pelo user-service.

        Raises:
            httpx.HTTPStatusError: Quando o user-service rejeita a alteração.
            httpx.RequestError: Quando ocorre uma falha de comunicação.
        """

        return await self.admin_user_client.update(
            access_token=access_token,
            user_id=user_id,
            payload=payload
        )

    async def delete(self,
                     access_token: str,
                     user_id: UUID) -> None:
        """
        Remove um usuário do user-service.

        Args:
            access_token: Token JWT da sessão administrativa.
            user_id: Identificador UUID do usuário removido.

        Raises:
            httpx.HTTPStatusError: Quando o user-service rejeita a remoção.
            httpx.RequestError: Quando ocorre uma falha de comunicação.
        """

        await self.admin_user_client.delete(
            access_token=access_token,
            user_id=user_id
        )


def get_user_service(
    admin_user_client: AdminUserClient = Depends(get_admin_user_client)
) -> UserService:
    """
    Fornece o serviço administrativo de usuários por injeção de dependência.

    Args:
        admin_user_client: Cliente configurado para acessar o user-service.

    Returns:
        Instância pronta para uso de `UserService`.
    """

    return UserService(admin_user_client=admin_user_client)
