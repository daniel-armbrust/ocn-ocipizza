#
# services/order_service.py
#

from uuid import UUID

from fastapi import Depends

from app.clients.order_client import OrderClient, get_order_client


class OrderService:
    """
    Coordena as consultas de pedidos utilizadas pelo painel do usuário.
    """

    def __init__(self, order_client: OrderClient) -> None:
        """
        Inicializa o serviço com o cliente do order-service.

        Args:
            order_client: Cliente HTTP utilizado para consultar pedidos.

        Returns:
            None.
        """

        self.order_client = order_client

    async def get_all(self,
                      access_token: str,
                      limit: int = 20,
                      offset: int = 0) -> list[dict]:
        """
        Obtém os pedidos pertencentes ao usuário autenticado.

        Args:
            access_token: Token JWT do usuário autenticado.
            limit: Quantidade máxima de pedidos retornados.
            offset: Quantidade de pedidos ignorados antes da consulta.

        Returns:
            Lista de pedidos retornada pelo order-service.

        Raises:
            httpx.HTTPStatusError: Caso o order-service rejeite a consulta.
            httpx.RequestError: Caso o order-service esteja indisponível.
        """

        return await self.order_client.get_all(
            access_token=access_token,
            limit=limit,
            offset=offset
        )

    async def get_by_id(self,
                        access_token: str,
                        order_id: UUID) -> dict:
        """
        Obtém um pedido pertencente ao usuário autenticado.

        Args:
            access_token: Token JWT do usuário autenticado.
            order_id: Identificador do pedido consultado.

        Returns:
            Pedido retornado pelo order-service.

        Raises:
            httpx.HTTPStatusError: Caso o order-service rejeite a consulta.
            httpx.RequestError: Caso o order-service esteja indisponível.
        """

        return await self.order_client.get_by_id(
            access_token=access_token,
            order_id=order_id
        )


def get_order_service(
    order_client: OrderClient = Depends(get_order_client)
) -> OrderService:
    """
    Fornece o serviço responsável pelas consultas de pedidos.

    Args:
        order_client: Cliente configurado para acessar o order-service.

    Returns:
        Instância configurada de `OrderService`.
    """

    return OrderService(order_client=order_client)
