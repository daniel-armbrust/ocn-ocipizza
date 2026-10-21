#
# clients/pizza_client.py
#

import httpx

from app.config.settings import settings


class PizzaClient:
    """
    Cliente responsável pela comunicação com o pizza-service.
    """
    def __init__(self, base_url: str) -> None:
        """
        Inicializa o cliente com a URL do pizza-service.

        Args:
            base_url: URL-base utilizada nas chamadas ao serviço.

        Returns:
            None.
        """

        self.base_url = base_url.rstrip('/')

    async def get_all(self,
                      category: str | None = None,
                      available: bool | None = None,
                      limit: int = 10,
                      offset: int = 0) -> dict:
        """
        Retorna as pizzas disponibilizadas pelo pizza-service.

        Args:
            category: Categoria utilizada para filtrar as pizzas.
            available: Indica se devem ser retornadas pizzas disponíveis
                ou indisponíveis.
            limit: Quantidade máxima de registros retornados.
            offset: Quantidade de registros ignorados antes da consulta.

        Returns:
            Lista contendo as pizzas retornadas pelo pizza-service.

        Raises:
            httpx.HTTPStatusError: Caso o pizza-service retorne
                uma resposta HTTP de erro.
            httpx.RequestError: Caso ocorra uma falha de comunicação
                com o pizza-service.
        """

        # Define os parâmetros obrigatórios utilizados para paginação.
        params = {
            'limit': limit,
            'offset': offset
        }

        # Adiciona a categoria somente quando informada.
        if category is not None:
            params['category'] = category

        # Adiciona o filtro de disponibilidade somente quando informado.
        if available is not None:
            params['available'] = available

        # O cliente assíncrono evita bloquear o event loop enquanto o
        # frontend-service aguarda a resposta do pizza-service.
        async with httpx.AsyncClient(
             timeout=settings.http_client_timeout
        ) as client:
            response = await client.get(
                f'{self.base_url}/pizzas',
                params=params,
                timeout=settings.http_client_timeout
            )

        # Converte respostas HTTP de erro em exceções.
        response.raise_for_status()

        # Retorna integralmente o JSON produzido pelo pizza-service.
        return response.json()

    async def get_by_id(self, pizza_id: str) -> dict:
        """
        Obtém uma pizza específica pelo seu identificador.

        Args:
            pizza_id: Identificador UUID da pizza consultada.

        Returns:
            Dados da pizza retornados pelo pizza-service.

        Raises:
            httpx.HTTPStatusError: Caso o pizza-service retorne uma resposta
                HTTP de erro.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                pizza-service.
        """

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.get(
                f'{self.base_url}/pizzas/{pizza_id}',
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

        pizza = response.json()['data']['pizza']

        # A imagem é privada no Object Storage e deve ser acessada através
        # da rota de imagem do frontend-service.
        pizza['image_url'] = f'/pizzas/{pizza_id}/image'

        return pizza

    async def get_image(self, pizza_id: str) -> tuple[bytes, str]:
        """
        Obtém o conteúdo da imagem de uma pizza.

        Args:
            pizza_id: Identificador UUID da pizza consultada.

        Returns:
            Tupla contendo os bytes da imagem e o seu tipo MIME.

        Raises:
            httpx.HTTPStatusError: Caso o pizza-service retorne uma resposta
                HTTP de erro.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                pizza-service.
        """

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.get(
                f'{self.base_url}/pizzas/{pizza_id}/image',
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

        content_type = response.headers.get('content-type', '')

        # A rota de imagem não deve encaminhar respostas genéricas ou
        # arquivos que não sejam imagens para o navegador.
        if not content_type.startswith('image/'):
            raise ValueError(
                'Pizza image response must have an image content type.'
            )

        return response.content, content_type

def get_pizza_client() -> PizzaClient:
    """
    Fornece o cliente utilizado para comunicação com o 
    pizza-service.

    Returns:
        Instância configurada de `PizzaClient`.
    """

    return PizzaClient(
        base_url=settings.pizza_service_url
    )
