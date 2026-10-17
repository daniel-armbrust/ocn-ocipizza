#
# services/delivery_service.py
#

from typing import Any
from uuid import UUID

from fastapi import Depends

from app.clients.admin_delivery_client import (
    AdminDeliveryClient,
    get_admin_delivery_client
)


class DeliveryService:
    """
    Coordena as operações administrativas das áreas de entrega.

    A autorização permanece nas dependências das rotas. Este serviço
    concentra os casos de uso e a comunicação com o delivery-service.
    """

    def __init__(self, admin_delivery_client: AdminDeliveryClient) -> None:
        """
        Inicializa o serviço com o cliente do delivery-service.

        Args:
            admin_delivery_client: Cliente HTTP utilizado nas operações
                administrativas de entrega.

        Returns:
            None.
        """

        self.admin_delivery_client = admin_delivery_client

    async def get_all(self,
                      access_token: str,
                      active: bool | None = None,
                      limit: int = 50,
                      offset: int = 0) -> list[dict]:
        """
        Obtém as áreas de entrega disponíveis para administração.

        Args:
            access_token: Token JWT da sessão administrativa.
            active: Status utilizado como filtro opcional.
            limit: Quantidade máxima de áreas retornadas.
            offset: Quantidade de áreas ignoradas antes da consulta.

        Returns:
            Lista de áreas retornada pelo delivery-service.

        Raises:
            httpx.HTTPStatusError: Quando o delivery-service rejeita a
                consulta.
            httpx.RequestError: Quando o delivery-service está indisponível.
        """

        return await self.admin_delivery_client.get_all(
            access_token=access_token,
            active=active,
            limit=limit,
            offset=offset
        )

    async def get_by_id(self,
                        access_token: str,
                        delivery_area_id: UUID) -> dict:
        """
        Obtém uma área de entrega pelo seu identificador.

        Args:
            access_token: Token JWT da sessão administrativa.
            delivery_area_id: Identificador UUID da área consultada.

        Returns:
            Área de entrega retornada pelo delivery-service.

        Raises:
            httpx.HTTPStatusError: Quando o delivery-service rejeita a
                consulta.
            httpx.RequestError: Quando o delivery-service está indisponível.
        """

        return await self.admin_delivery_client.get_by_id(
            access_token=access_token,
            delivery_area_id=delivery_area_id
        )

    async def create(self,
                     access_token: str,
                     payload: dict[str, Any]) -> dict:
        """
        Cria uma área de entrega.

        Args:
            access_token: Token JWT da sessão administrativa.
            payload: Dados validados da área de entrega.

        Returns:
            Área de entrega criada pelo delivery-service.

        Raises:
            httpx.HTTPStatusError: Quando o delivery-service rejeita os dados.
            httpx.RequestError: Quando o delivery-service está indisponível.
        """

        return await self.admin_delivery_client.create(
            access_token=access_token,
            payload=payload
        )

    async def update(self,
                     access_token: str,
                     delivery_area_id: UUID,
                     payload: dict[str, Any]) -> dict:
        """
        Atualiza uma área de entrega existente.

        Args:
            access_token: Token JWT da sessão administrativa.
            delivery_area_id: Identificador UUID da área atualizada.
            payload: Dados validados para atualização da área.

        Returns:
            Área de entrega atualizada pelo delivery-service.

        Raises:
            httpx.HTTPStatusError: Quando o delivery-service rejeita os dados.
            httpx.RequestError: Quando o delivery-service está indisponível.
        """

        return await self.admin_delivery_client.update(
            access_token=access_token,
            delivery_area_id=delivery_area_id,
            payload=payload
        )

    async def delete(self,
                     access_token: str,
                     delivery_area_id: UUID) -> None:
        """
        Remove uma área de entrega.

        Args:
            access_token: Token JWT da sessão administrativa.
            delivery_area_id: Identificador UUID da área removida.

        Returns:
            None.

        Raises:
            httpx.HTTPStatusError: Quando o delivery-service rejeita a
                remoção.
            httpx.RequestError: Quando o delivery-service está indisponível.
        """

        await self.admin_delivery_client.delete(
            access_token=access_token,
            delivery_area_id=delivery_area_id
        )

    async def set_active(self,
                         access_token: str,
                         delivery_area_id: UUID,
                         active: bool) -> dict:
        """
        Atualiza somente o status de uma área de entrega.

        Args:
            access_token: Token JWT da sessão administrativa.
            delivery_area_id: Identificador UUID da área atualizada.
            active: Indica se a área deve ficar disponível para pedidos.

        Returns:
            Área de entrega atualizada pelo delivery-service.

        Raises:
            httpx.HTTPStatusError: Quando o delivery-service rejeita a
                alteração.
            httpx.RequestError: Quando o delivery-service está indisponível.
        """

        return await self.admin_delivery_client.set_active(
            access_token=access_token,
            delivery_area_id=delivery_area_id,
            active=active
        )


def get_delivery_service(
    admin_delivery_client: AdminDeliveryClient = Depends(
        get_admin_delivery_client
    )
) -> DeliveryService:
    """
    Fornece o serviço administrativo de áreas de entrega.

    Args:
        admin_delivery_client: Cliente configurado para acessar o
            delivery-service.

    Returns:
        Instância configurada de `DeliveryService`.
    """

    return DeliveryService(
        admin_delivery_client=admin_delivery_client
    )
