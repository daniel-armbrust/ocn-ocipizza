#
# clients/admin_delivery_client.py
#

from typing import Any
from uuid import UUID

import httpx

from app.config.settings import settings


class AdminDeliveryClient:
    """
    Cliente responsável pela comunicação com o delivery-service.
    """

    def __init__(self, base_url: str) -> None:
        """
        Inicializa o cliente com a URL do delivery-service.

        Args:
            base_url: URL-base utilizada nas chamadas ao serviço.

        Returns:
            None.
        """

        self.base_url = base_url.rstrip('/')

    async def get_all(self,
                      access_token: str,
                      active: bool | None = None,
                      limit: int = 50,
                      offset: int = 0) -> list[dict]:
        """
        Retorna as áreas de entrega cadastradas.

        Args:
            access_token: Token de acesso JWT da sessão administrativa.
            active: Status utilizado como filtro opcional.
            limit: Quantidade máxima de áreas retornadas.
            offset: Quantidade de áreas ignoradas antes da consulta.

        Returns:
            Áreas retornadas pelo delivery-service.

        Raises:
            httpx.HTTPStatusError: Caso o delivery-service retorne uma
                resposta HTTP de erro.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                delivery-service.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        params: dict[str, bool | int] = {
            'limit': limit,
            'offset': offset
        }

        if active is not None:
            params['active'] = active

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.get(
                f'{self.base_url}/admin/delivery/areas',
                params=params,
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

        return response.json()['data']['delivery_areas']

    async def get_by_id(self,
                        access_token: str,
                        delivery_area_id: UUID) -> dict:
        """
        Retorna uma área de entrega pelo identificador.

        Args:
            access_token: Token de acesso JWT da sessão administrativa.
            delivery_area_id: Identificador UUID da área consultada.

        Returns:
            Área retornada pelo delivery-service.

        Raises:
            httpx.HTTPStatusError: Caso o delivery-service retorne uma
                resposta HTTP de erro.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                delivery-service.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.get(
                f'{self.base_url}/admin/delivery/areas/{delivery_area_id}',
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

        return response.json()['data']['delivery_area']

    async def create(self,
                     access_token: str,
                     payload: dict[str, Any]) -> dict:
        """
        Cria uma área de entrega.

        Args:
            access_token: Token de acesso JWT da sessão administrativa.
            payload: Dados da área de entrega validados pelo formulário.

        Returns:
            Área criada pelo delivery-service.

        Raises:
            httpx.HTTPStatusError: Caso o delivery-service rejeite os dados.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                delivery-service.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.post(
                f'{self.base_url}/admin/delivery/areas',
                json=payload,
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

        return response.json()['data']['delivery_area']

    async def update(self,
                     access_token: str,
                     delivery_area_id: UUID,
                     payload: dict[str, Any]) -> dict:
        """
        Atualiza uma área de entrega.

        Args:
            access_token: Token de acesso JWT da sessão administrativa.
            delivery_area_id: Identificador UUID da área atualizada.
            payload: Dados da área de entrega que serão atualizados.

        Returns:
            Área atualizada pelo delivery-service.

        Raises:
            httpx.HTTPStatusError: Caso o delivery-service rejeite os dados.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                delivery-service.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.put(
                f'{self.base_url}/admin/delivery/areas/{delivery_area_id}',
                json=payload,
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

        return response.json()['data']['delivery_area']

    async def delete(self,
                     access_token: str,
                     delivery_area_id: UUID) -> None:
        """
        Remove uma área de entrega.

        Args:
            access_token: Token de acesso JWT da sessão administrativa.
            delivery_area_id: Identificador UUID da área removida.

        Raises:
            httpx.HTTPStatusError: Caso o delivery-service rejeite a remoção.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                delivery-service.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.delete(
                f'{self.base_url}/admin/delivery/areas/{delivery_area_id}',
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

    async def set_active(self,
                         access_token: str,
                         delivery_area_id: UUID,
                         active: bool) -> dict:
        """
        Atualiza somente o status de uma área de entrega.

        Args:
            access_token: Token de acesso JWT da sessão administrativa.
            delivery_area_id: Identificador UUID da área atualizada.
            active: Novo status da área de entrega.

        Returns:
            Área atualizada pelo delivery-service.

        Raises:
            httpx.HTTPStatusError: Caso o delivery-service rejeite a alteração.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                delivery-service.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.patch(
                f'{self.base_url}/admin/delivery/areas/{delivery_area_id}/active',
                params={'active': active},
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

        return response.json()['data']['delivery_area']


def get_admin_delivery_client() -> AdminDeliveryClient:
    """
    Fornece o cliente utilizado para comunicação com o delivery-service.

    Returns:
        Instância configurada de `AdminDeliveryClient`.
    """

    return AdminDeliveryClient(
        base_url=settings.delivery_service_url
    )
