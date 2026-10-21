#
# clients/admin_pizza_client.py
#

from decimal import Decimal
from uuid import UUID

import httpx

from app.config.settings import settings


class AdminPizzaClient:
    """
    Cliente HTTP utilizado para operar o catálogo no pizza-service.

    Esta classe concentra os detalhes técnicos das requisições externas,
    mantendo URLs, cabeçalhos e interpretação das respostas fora das rotas.
    """

    def __init__(self, base_url: str) -> None:
        """
        Inicializa o cliente com a URL base do pizza-service.

        Args:
            base_url: URL usada como prefixo nas requisições HTTP.
        """

        # Remove a barra final para evitar URLs duplicadas ao concatenar os
        # caminhos dos endpoints.
        self.base_url = base_url.rstrip('/')

    async def get_all(self,
                      access_token: str,
                      category: str | None = None,
                      available: bool | None = None,
                      limit: int = 50,
                      offset: int = 0) -> list[dict]:
        """
        Obtém as pizzas cadastradas no pizza-service.

        Args:
            access_token: Token JWT da sessão administrativa.
            category: Categoria utilizada como filtro opcional.
            available: Disponibilidade utilizada como filtro opcional.
            limit: Quantidade máxima de pizzas retornadas.
            offset: Quantidade de registros ignorados.

        Raises:
            httpx.HTTPError: Quando a comunicação falha ou o pizza-service
                retorna uma resposta HTTP de erro.

        Returns:
            Lista de pizzas retornada pelo pizza-service.
        """

        # Os parâmetros opcionais só são enviados quando foram informados,
        # evitando alterar o significado dos filtros no serviço externo.
        params: dict[str, str | int | bool] = {
            'limit': limit,
            'offset': offset
        }

        if category:
            params['category'] = category

        if available is not None:
            params['available'] = available

        # O token da sessão é convertido no cabeçalho padrão de autenticação.
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        # O cliente assíncrono evita bloquear o event loop enquanto aguarda a
        # resposta do pizza-service.
        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.get(
                f'{self.base_url}/pizzas',
                params=params,
                headers=headers,
                timeout=settings.http_client_timeout
            )

        # Converte respostas HTTP de erro em exceções tratáveis pelas camadas
        # de serviço e de rotas do admin-service.
        response.raise_for_status()

        return response.json()['data']['pizzas']

    async def get_by_id(self,
                        access_token: str,
                        pizza_id: UUID) -> dict:
        """
        Obtém os dados de uma pizza pelo identificador.

        Args:
            access_token: Token JWT da sessão administrativa.
            pizza_id: Identificador único da pizza consultada.

        Raises:
            httpx.HTTPError: Quando a comunicação falha ou o pizza-service
                retorna uma resposta HTTP de erro.

        Returns:
            Dicionário com os dados da pizza consultada.
        """

        # O token permanece no cabeçalho; o UUID compõe o caminho do recurso.
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.get(
                f'{self.base_url}/pizzas/{pizza_id}',
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

        return response.json()['data']['pizza']

    async def get_image(self,
                        access_token: str,
                        pizza_id: UUID) -> tuple[bytes, str]:
        """
        Obtém a imagem de uma pizza no pizza-service.

        Args:
            access_token: Token JWT da sessão administrativa.
            pizza_id: Identificador único da pizza consultada.

        Raises:
            httpx.HTTPError: Quando a comunicação falha ou o pizza-service
                retorna uma resposta HTTP de erro.
            ValueError: Quando a resposta não possui um tipo MIME de imagem.

        Returns:
            Tupla contendo o conteúdo binário e o tipo MIME da imagem.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.get(
                f'{self.base_url}/pizzas/{pizza_id}/image',
                headers=headers,
                timeout=settings.http_client_timeout
            )

        response.raise_for_status()

        content_type = response.headers.get('content-type', '')

        if not content_type.startswith('image/'):
            raise ValueError(
                'Pizza image response must have an image content type.'
            )

        return response.content, content_type

    async def create(self,
                     access_token: str,
                     data: dict,
                     image: tuple) -> dict:
        """
        Cria uma pizza no pizza-service.

        Args:
            access_token: Token JWT da sessão administrativa.
            data: Campos textuais e numéricos enviados no formulário.
            image: Tupla multipart com nome, conteúdo e tipo do arquivo.

        Raises:
            httpx.HTTPError: Quando a comunicação falha ou o pizza-service
                retorna uma resposta HTTP de erro.

        Returns:
            Dicionário com os dados da pizza criada.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        # O WTForms representa o preço como `Decimal`, mas o httpx exige
        # tipos primitivos para os campos do multipart/form-data.
        multipart_data = {
            field: format(value, 'f') if isinstance(value, Decimal) else value
            for field, value in data.items()
        }

        # `files` e `data` fazem com que o httpx monte uma requisição
        # multipart/form-data compatível com o endpoint de criação.
        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.post(
                f'{self.base_url}/admin/pizzas',
                data=multipart_data,
                files={'image': image},
                headers=headers
            )

        response.raise_for_status()

        return response.json()['data']['pizza']

    async def update(self, access_token: str, pizza_id: UUID,
                     data: dict, image: tuple | None = None) -> dict:
        """
        Atualiza os dados de uma pizza no pizza-service.

        Args:
            access_token: Token JWT da sessão administrativa.
            pizza_id: Identificador único da pizza atualizada.
            data: Campos que devem ser atualizados.
            image: Tupla multipart opcional com a nova imagem.

        Raises:
            httpx.HTTPError: Quando a comunicação falha ou o pizza-service
                retorna uma resposta HTTP de erro.

        Returns:
            Dicionário com os dados atualizados da pizza.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        # Mantém a mesma conversão usada na criação para que atualizações de
        # preço também possam ser enviadas pelo encoder multipart do httpx.
        multipart_data = {
            field: format(value, 'f') if isinstance(value, Decimal) else value
            for field, value in data.items()
        }

        # Quando não há imagem nova, o campo `files` não é enviado e o
        # pizza-service mantém a imagem atual do registro.
        files = {'image': image} if image else None

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.put(
                f'{self.base_url}/admin/pizzas/{pizza_id}',
                data=multipart_data,
                files=files,
                headers=headers
            )
        response.raise_for_status()

        return response.json()['data']['pizza']

    async def delete(self,
                     access_token: str,
                     pizza_id: UUID) -> None:
        """
        Exclui uma pizza do catálogo do pizza-service.

        Args:
            access_token: Token JWT da sessão administrativa.
            pizza_id: Identificador único da pizza que será excluída.

        Raises:
            httpx.HTTPError: Quando a comunicação falha ou o pizza-service
                retorna uma resposta HTTP de erro.

        Returns:
            None: A resposta de exclusão não possui dados de negócio usados
                pelo admin-service.
        """

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.delete(
                f'{self.base_url}/admin/pizzas/{pizza_id}',
                headers=headers
            )

        response.raise_for_status()


def get_admin_pizza_client() -> AdminPizzaClient:
    """
    Fornece o cliente configurado do pizza-service.

    Returns:
        Instância de `AdminPizzaClient` configurada com a URL do serviço.
    """

    return AdminPizzaClient(
        base_url=settings.pizza_service_url
    )
