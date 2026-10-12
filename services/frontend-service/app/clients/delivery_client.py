#
# clients/delivery_client.py
#

import httpx

from app.config.settings import settings


class DeliveryClient:
    """
    Cliente responsável pela consulta de cotações de entrega junto ao
    delivery-service.
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

    async def get_quote(self,
                        access_token: str,
                        zip_code: str) -> dict:
        """
        Consulta a disponibilidade e os valores de entrega para um CEP.

        Args:
            access_token: Token de acesso JWT do usuário autenticado.
            zip_code: CEP utilizado para consultar a entrega.

        Returns:
            Cotação contendo disponibilidade, taxa e prazo estimado.

        Raises:
            httpx.HTTPStatusError: Caso o delivery-service retorne uma
                resposta HTTP de erro.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                delivery-service.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        # Utiliza um cliente assíncrono para não bloquear o event loop
        # enquanto o frontend-service aguarda a resposta da cotação.
        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.get(
                f'{self.base_url}/delivery/quote/{zip_code}',
                headers=headers,
                timeout=settings.http_client_timeout
            )

        # Converte respostas HTTP de erro em exceções tratáveis pela rota.
        response.raise_for_status()

        # O delivery-service utiliza JSend; somente os dados da cotação são
        # devolvidos para simplificar o consumo pela camada de rotas.
        return response.json()['data']


def get_delivery_client() -> DeliveryClient:
    """
    Fornece o cliente utilizado para comunicação com o delivery-service.

    Returns:
        Instância configurada de `DeliveryClient`.
    """

    return DeliveryClient(
        base_url=settings.delivery_service_url
    )
