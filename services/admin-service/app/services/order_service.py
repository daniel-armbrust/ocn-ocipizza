#
# services/order_service.py
#

from uuid import UUID

from fastapi import Depends

from app.clients.admin_order_client import (
    AdminOrderClient,
    get_admin_order_client
)


class OrderService:
    """
    Coordena as operações de pedidos dos painéis administrativo e da cozinha.

    A autorização de cada perfil permanece nas dependências das rotas. Este
    serviço concentra somente a comunicação e os casos de uso compartilhados
    relacionados aos pedidos.
    """

    def __init__(self, admin_order_client: AdminOrderClient) -> None:
        """
        Inicializa o serviço com o cliente do order-service.

        Args:
            admin_order_client: Cliente HTTP utilizado para consultar e
                atualizar pedidos.

        Returns:
            None.
        """

        self.admin_order_client = admin_order_client

    async def get_all(self,
                      access_token: str,
                      status: str | None = None,
                      payment_status: str | None = None,
                      limit: int = 50,
                      offset: int = 0) -> list[dict]:
        """
        Obtém os pedidos disponíveis para acompanhamento operacional.

        Args:
            access_token: Token JWT da sessão autenticada.
            status: Estado do pedido utilizado como filtro opcional.
            payment_status: Estado do pagamento utilizado como filtro
                opcional.
            limit: Quantidade máxima de pedidos retornados.
            offset: Quantidade de pedidos ignorados antes da consulta.

        Returns:
            Lista de pedidos retornada pelo order-service.

        Raises:
            httpx.HTTPStatusError: Quando o order-service rejeita a consulta.
            httpx.RequestError: Quando o order-service está indisponível.
        """

        return await self.admin_order_client.get_all(
            access_token=access_token,
            order_status=status.upper() if status else None,
            payment_status=(
                payment_status.upper()
                if payment_status
                else None
            ),
            limit=limit,
            offset=offset
        )

    async def get_by_id(self,
                        access_token: str,
                        order_id: UUID) -> dict:
        """
        Obtém um pedido para acompanhamento administrativo ou da cozinha.

        Args:
            access_token: Token JWT da sessão autenticada.
            order_id: Identificador UUID do pedido consultado.

        Returns:
            Pedido retornado pelo order-service.

        Raises:
            httpx.HTTPStatusError: Quando o order-service rejeita a consulta.
            httpx.RequestError: Quando o order-service está indisponível.
        """

        return await self.admin_order_client.get_by_id(
            access_token=access_token,
            order_id=order_id
        )

    async def get_summary(self, access_token: str) -> dict[str, int]:
        """
        Obtém os indicadores agregados do painel de pedidos.

        Args:
            access_token: Token JWT da sessão autenticada.

        Returns:
            Resumo calculado pelo order-service.

        Raises:
            httpx.HTTPStatusError: Quando o order-service rejeita a consulta.
            httpx.RequestError: Quando o order-service está indisponível.
        """

        return await self.admin_order_client.get_summary(
            access_token=access_token
        )

    async def update_status(self,
                            access_token: str,
                            order_id: UUID,
                            status: str) -> dict:
        """
        Atualiza o estado operacional de um pedido.

        Args:
            access_token: Token JWT da sessão autenticada.
            order_id: Identificador UUID do pedido atualizado.
            status: Novo estado do pedido.

        Returns:
            Pedido atualizado pelo order-service.

        Raises:
            httpx.HTTPStatusError: Quando o order-service rejeita a alteração.
            httpx.RequestError: Quando o order-service está indisponível.
        """

        return await self.admin_order_client.update_status(
            access_token=access_token,
            order_id=order_id,
            status=status.upper()
        )

    async def delete(self,
                     access_token: str,
                     order_id: UUID) -> None:
        """
        Remove um pedido através do order-service.

        Args:
            access_token: Token JWT da sessão administrativa.
            order_id: Identificador UUID do pedido removido.

        Raises:
            httpx.HTTPStatusError: Quando o order-service rejeita a remoção.
            httpx.RequestError: Quando o order-service está indisponível.
        """

        await self.admin_order_client.delete(
            access_token=access_token,
            order_id=order_id
        )


def get_order_service(
    admin_order_client: AdminOrderClient = Depends(
        get_admin_order_client
    )
) -> OrderService:
    """
    Fornece o serviço compartilhado de pedidos do admin-service.

    Args:
        admin_order_client: Cliente configurado para acessar o order-service.

    Returns:
        Instância configurada de `OrderService`.
    """

    return OrderService(
        admin_order_client=admin_order_client
    )
