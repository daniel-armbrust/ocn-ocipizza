#
# clients/order_client.py
#

from typing import Any
from uuid import UUID

import httpx

from app.config.settings import settings


class OrderClient:
    """
    Cliente responsável pela comunicação com o order-service.
    """

    def __init__(self, base_url: str) -> None:
        """
        Inicializa o cliente com a URL do order-service.

        Args:
            base_url: URL-base utilizada nas chamadas ao serviço.

        Returns:
            None.
        """

        self.base_url = base_url.rstrip('/')

    async def create(self,
                     access_token: str,
                     payload: dict[str, Any]) -> dict:
        """
        Cria um pedido para o usuário autenticado.

        Args:
            access_token: Token de acesso JWT do usuário autenticado.
            payload: Snapshots, itens, valores e chave de idempotência do
                pedido confirmado.

        Returns:
            Pedido criado ou recuperado de forma idempotente.

        Raises:
            httpx.HTTPStatusError: Caso o order-service retorne uma resposta
                HTTP de erro.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                order-service.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        # A chamada assíncrona evita bloquear o event loop enquanto o pedido
        # é validado e persistido pelo order-service.
        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.post(
                f'{self.base_url}/orders',
                json=payload,
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

        return response.json()['data']['order']

    async def get_all(self,
                      access_token: str,
                      limit: int = 10,
                      offset: int = 0) -> list[dict]:
        """
        Retorna os pedidos pertencentes ao usuário autenticado.

        Args:
            access_token: Token de acesso JWT do usuário autenticado.
            limit: Quantidade máxima de pedidos retornados.
            offset: Quantidade de pedidos ignorados antes da consulta.

        Returns:
            Pedidos retornados pelo order-service.

        Raises:
            httpx.HTTPStatusError: Caso o order-service retorne uma resposta
                HTTP de erro.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                order-service.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        params = {
            'limit': limit,
            'offset': offset
        }

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.get(
                f'{self.base_url}/orders',
                params=params,
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

        return response.json()['data']['orders']

    async def get_by_id(self,
                        access_token: str,
                        order_id: UUID) -> dict:
        """
        Retorna um pedido pertencente ao usuário autenticado.

        Args:
            access_token: Token de acesso JWT do usuário autenticado.
            order_id: Identificador UUID do pedido consultado.

        Returns:
            Pedido retornado pelo order-service.

        Raises:
            httpx.HTTPStatusError: Caso o order-service retorne uma resposta
                HTTP de erro.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                order-service.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.get(
                f'{self.base_url}/orders/{order_id}',
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

        return response.json()['data']['order']


def get_order_client() -> OrderClient:
    """
    Fornece o cliente utilizado para comunicação com o order-service.

    Returns:
        Instância configurada de `OrderClient`.
    """

    return OrderClient(
        base_url=settings.order_service_url
    )
