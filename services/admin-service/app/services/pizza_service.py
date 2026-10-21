#
# services/pizza_service.py
#

from fastapi import Depends
from uuid import UUID

from app.clients.admin_pizza_client import (
    AdminPizzaClient,
    get_admin_pizza_client
)


class PizzaService:
    """
    Coordena as operações do catálogo para o painel administrativo.

    A classe representa a camada de serviço do admin-service. Ela mantém as
    regras de orquestração fora das rotas e delega a comunicação HTTP ao
    cliente específico do pizza-service.
    """

    def __init__(self, admin_pizza_client: AdminPizzaClient) -> None:
        """
        Inicializa o serviço com o cliente usado na comunicação externa.

        Args:
            admin_pizza_client: Cliente HTTP responsável por chamar o
                pizza-service.
        """

        self.admin_pizza_client = admin_pizza_client

    async def get_all(self,
                      access_token: str,
                      category: str | None = None,
                      available: bool | None = None,
                      limit: int = 50,
                      offset: int = 0) -> list[dict]:
        """
        Obtém uma página de pizzas do pizza-service.

        Args:
            access_token: Token JWT da sessão administrativa.
            category: Categoria opcional usada para filtrar o catálogo.
            available: Disponibilidade opcional usada para filtrar as pizzas.
            limit: Quantidade máxima de registros solicitados.
            offset: Quantidade de registros ignorados antes da página atual.

        Raises:
            httpx.HTTPError: Quando o cliente não consegue concluir a
                comunicação ou recebe uma resposta HTTP de erro.

        Returns:
            Lista de pizzas retornada pelo pizza-service.
        """

        # A paginação e os filtros são encaminhados ao cliente HTTP, que
        # conhece o contrato técnico do endpoint externo.
        return await self.admin_pizza_client.get_all(
            access_token=access_token,
            category=category,
            available=available,
            limit=limit,
            offset=offset
        )

    async def get_by_id(self,
                        access_token: str,
                        pizza_id: UUID) -> dict:
        """
        Obtém uma pizza específica para exibição administrativa.

        Args:
            access_token: Token JWT da sessão administrativa.
            pizza_id: Identificador único da pizza consultada.

        Raises:
            httpx.HTTPError: Quando o cliente não consegue concluir a
                comunicação ou recebe uma resposta HTTP de erro.

        Returns:
            Dicionário com os dados da pizza retornados pelo pizza-service.
        """

        # A rota trabalha com UUIDs; o cliente converte o identificador para
        # a URL do endpoint sem duplicar essa responsabilidade aqui.
        return await self.admin_pizza_client.get_by_id(
            access_token=access_token,
            pizza_id=pizza_id
        )

    async def get_image(self,
                        access_token: str,
                        pizza_id: UUID) -> tuple[bytes, str]:
        """
        Obtém a imagem de uma pizza através do pizza-service.

        Args:
            access_token: Token JWT da sessão administrativa.
            pizza_id: Identificador único da pizza consultada.

        Raises:
            httpx.HTTPError: Quando o cliente não consegue concluir a
                comunicação ou recebe uma resposta HTTP de erro.
            ValueError: Quando a resposta não possui um tipo MIME de imagem.

        Returns:
            Tupla contendo o conteúdo binário e o tipo MIME da imagem.
        """

        return await self.admin_pizza_client.get_image(
            access_token=access_token,
            pizza_id=pizza_id
        )

    async def create(self,
                    access_token: str,
                    data: dict,
                    image: tuple) -> dict:
        """
        Cria uma pizza no catálogo do pizza-service.

        Args:
            access_token: Token JWT da sessão administrativa.
            data: Campos textuais e numéricos da pizza.
            image: Tupla multipart contendo nome, conteúdo e tipo do arquivo.

        Raises:
            httpx.HTTPError: Quando a criação falha na comunicação com o
                pizza-service ou o serviço retorna um erro HTTP.

        Returns:
            Dicionário com os dados da pizza criada.
        """

        # O arquivo é enviado separadamente dos campos para preservar o
        # contrato multipart/form-data do endpoint de criação.
        return await self.admin_pizza_client.create(access_token, data, image)

    async def update(self, access_token: str, pizza_id: UUID,
                     data: dict, image: tuple | None = None) -> dict:
        """
        Atualiza os dados de uma pizza e, opcionalmente, sua imagem.

        Args:
            access_token: Token JWT da sessão administrativa.
            pizza_id: Identificador único da pizza que será atualizada.
            data: Campos da pizza que devem ser atualizados.
            image: Tupla multipart opcional com a nova imagem.

        Raises:
            httpx.HTTPError: Quando a atualização falha na comunicação com o
                pizza-service ou o serviço retorna um erro HTTP.

        Returns:
            Dicionário com os dados atualizados da pizza.
        """

        # Quando não há nova imagem, o cliente envia apenas os campos do
        # formulário e preserva a imagem já cadastrada no pizza-service.
        return await self.admin_pizza_client.update(
            access_token, pizza_id, data, image
        )

    async def delete(self, access_token: str, pizza_id: UUID) -> None:
        """
        Remove uma pizza do catálogo.

        Args:
            access_token: Token JWT da sessão administrativa.
            pizza_id: Identificador único da pizza que será removida.

        Raises:
            httpx.HTTPError: Quando a exclusão falha na comunicação com o
                pizza-service ou o serviço retorna um erro HTTP.

        Returns:
            None: A operação é concluída sem corpo de resposta de negócio.
        """

        # A confirmação da exclusão é feita pela rota antes desta chamada;
        # aqui apenas delegamos a operação ao cliente do serviço externo.
        await self.admin_pizza_client.delete(access_token, pizza_id)


def get_pizza_service(
    admin_pizza_client: AdminPizzaClient = Depends(get_admin_pizza_client)
) -> PizzaService:
    """
    Fornece o serviço de pizzas por injeção de dependência.

    Args:
        admin_pizza_client: Cliente HTTP configurado para o pizza-service.

    Returns:
        Instância de `PizzaService` pronta para uso pelas rotas.
    """

    # A dependência mantém a criação do cliente fora das rotas e facilita a
    # substituição da implementação em outros ambientes.
    return PizzaService(admin_pizza_client=admin_pizza_client)
