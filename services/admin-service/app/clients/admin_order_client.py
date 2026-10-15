#
# clients/admin_order_client.py
#

from typing import Any
from uuid import UUID

import httpx

from app.config.settings import settings


class AdminOrderClient:
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
                      order_status: str | None = None,
                      payment_status: str | None = None,
                      limit: int = 50,
                      offset: int = 0) -> list[dict]:
        """
        Retorna os pedidos disponíveis para acompanhamento operacional.

        Args:
            access_token: Token de acesso JWT do usuário autenticado.
            order_status: Estado do pedido utilizado como filtro opcional.
            payment_status: Estado do pagamento utilizado como filtro
                opcional.
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
        params: dict[str, str | int] = {
            'limit': limit,
            'offset': offset
        }

        if order_status:
            params['order_status'] = order_status

        if payment_status:
            params['payment_status'] = payment_status

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.get(
                f'{self.base_url}/admin/orders',
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
        Retorna um pedido para acompanhamento operacional.

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
                f'{self.base_url}/admin/orders/{order_id}',
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

        return response.json()['data']['order']

    async def get_summary(self, access_token: str) -> dict[str, int]:
        """
        Retorna os indicadores agregados do painel de pedidos.

        Args:
            access_token: Token de acesso JWT do usuário autenticado.

        Returns:
            Resumo retornado pelo order-service.

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
                f'{self.base_url}/admin/orders/summary',
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

        return response.json()['data']['summary']

    async def update_status(self,
                            access_token: str,
                            order_id: UUID,
                            status: str) -> dict:
        """
        Atualiza administrativamente o estado de um pedido.

        Args:
            access_token: Token de acesso JWT do usuário autenticado.
            order_id: Identificador UUID do pedido atualizado.
            status: Novo estado do pedido.

        Returns:
            Pedido atualizado pelo order-service.

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
            response = await client.patch(
                f'{self.base_url}/admin/orders/{order_id}/status',
                json={'status': status},
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

        return response.json()['data']['order']

    async def delete(self,
                     access_token: str,
                     order_id: UUID) -> None:
        """
        Remove administrativamente um pedido.

        Args:
            access_token: Token de acesso JWT da sessão administrativa.
            order_id: Identificador UUID do pedido removido.

        Raises:
            httpx.HTTPStatusError: Caso o order-service rejeite a remoção.
            httpx.RequestError: Caso ocorra uma falha de comunicação.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.delete(
                f'{self.base_url}/admin/orders/{order_id}',
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()


def get_admin_order_client() -> AdminOrderClient:
    """
    Fornece o cliente utilizado para comunicação com o order-service.

    Returns:
        Instância configurada de `OrderClient`.
    """

    return AdminOrderClient(
        base_url=settings.order_service_url
    )
