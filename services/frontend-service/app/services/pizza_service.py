#
# services/pizza_service.py
#

from fastapi import Depends

from app.clients.pizza_client import PizzaClient, get_pizza_client


class PizzaService:
    """
    Coordena os casos de uso do cardápio de pizzas no BFF.

    O serviço mantém as rotas independentes dos detalhes de comunicação com
    o pizza-service sem conhecer parâmetros HTTP, mensagens ou templates.
    """

    def __init__(self, pizza_client: PizzaClient) -> None:
        """
        Inicializa o serviço com o cliente do pizza-service.

        Args:
            pizza_client: Cliente utilizado para consultar a API de pizzas.

        Returns:
            None.
        """

        self.pizza_client = pizza_client

    async def get_all(self,
                      category: str | None = None,
                      available: bool | None = None,
                      limit: int = 10,
                      offset: int = 0) -> dict:
        """
        Retorna uma página de pizzas do cardápio.

        Args:
            category: Categoria utilizada como filtro opcional.
            available: Disponibilidade utilizada como filtro opcional.
            limit: Quantidade máxima de pizzas retornadas.
            offset: Quantidade de pizzas ignoradas antes da consulta.

        Returns:
            Resposta JSend contendo as pizzas retornadas pelo pizza-service.

        Raises:
            httpx.HTTPStatusError: Caso o pizza-service retorne uma resposta
                HTTP de erro.
            httpx.RequestError: Caso ocorra uma falha de comunicação com o
                pizza-service.
        """

        return await self.pizza_client.get_all(
            category=category,
            available=available,
            limit=limit,
            offset=offset
        )

    async def get_image(self, pizza_id: str) -> tuple[bytes, str]:
        """
        Obtém a imagem de uma pizza através do pizza-service.

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

        return await self.pizza_client.get_image(pizza_id)


def get_pizza_service(
    pizza_client: PizzaClient = Depends(get_pizza_client)
) -> PizzaService:
    """
    Fornece o serviço responsável pelos casos de uso do cardápio no BFF.

    Args:
        pizza_client: Cliente configurado para acessar o pizza-service.

    Returns:
        Instância configurada de `PizzaService`.
    """

    return PizzaService(pizza_client=pizza_client)
