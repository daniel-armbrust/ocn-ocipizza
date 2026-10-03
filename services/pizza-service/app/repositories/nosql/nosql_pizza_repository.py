#
# repositories/nosql/nosql_pizza_repository.py
#

from uuid import UUID

from borneo import (
    DeleteRequest,
    GetRequest,
    NoSQLHandle,
    PutOption,
    PutRequest,
    QueryRequest
)

from app.models.pizza import Pizza, PizzaCategory
from app.repositories.pizza_repository import PizzaRepository


class NosqlPizzaRepository(PizzaRepository):
    """
    Implementação do repositório de pizzas utilizando Oracle NoSQL.

    Esta classe traduz os modelos utilizados pela aplicação para o
    formato de dados utilizado pelo Oracle NoSQL Database.

    O repositório conhece os detalhes específicos da tecnologia de
    persistência, enquanto a camada de serviço continua dependente
    apenas da abstração `PizzaRepository`.
    """

    # TODO: Tratar exceções específicas do Oracle NoSQL relacionadas
    # a limites de leitura/escrita, throttling e indisponibilidade
    # temporária, incluindo estratégia de retry quando apropriado.

    def __init__(self, 
                 handle: NoSQLHandle,
                 table_name: str = 'pizzas') -> None:
        """
        Inicializa o repositório.

        Args:
            handle: Handle utilizado para executar operações no
                Oracle NoSQL Database.
            table_name: Nome da tabela utilizada para armazenar
                os dados das pizzas.

        Returns:
            None.
        """

        self.handle = handle
        self.table_name = table_name

    def create(self, pizza: Pizza) -> Pizza:
        """
        Persiste uma nova pizza.

        Args:
            pizza: Modelo contendo os dados da pizza que será persistida.

        Returns:
            Pizza persistida.
        """

        # O Oracle NoSQL não possui um tipo UUID específico.
        # O identificador é armazenado como string.
        row = self._to_row(pizza)

        # IF_ABSENT garante que uma pizza com o mesmo identificador
        # não seja sobrescrita acidentalmente durante a criação.
        request = (
            PutRequest()
            .set_table_name(self.table_name)
            .set_value(row)
            .set_option(PutOption.IF_ABSENT)
        )

        result = self.handle.put(request)

        # Uma operação de escrita bem-sucedida retorna uma versão
        # associada ao registro persistido.
        if result.get_version() is None:
            raise RuntimeError(
                'Error creating pizza in Oracle NoSQL.'
            )

        return pizza

    def get_by_id(self, pizza_id: UUID) -> Pizza | None:
        """
        Retorna uma pizza através de seu identificador.

        Args:
            pizza_id: Identificador UUID da pizza.

        Returns:
            Pizza encontrada ou `None` caso não exista.
        """

        # Como `id` é a chave primária da tabela, GetRequest é utilizado
        # diretamente em vez de executar uma consulta SQL.
        request = (
            GetRequest()
            .set_table_name(self.table_name)
            .set_key({'id': str(pizza_id)})
        )

        result = self.handle.get(request)

        row = result.get_value()

        if row is None:
            return None

        return self._to_model(row)

    def get_all(self,
                category: PizzaCategory | None = None,
                available: bool | None = None,
                limit: int = 10,
                offset: int = 0) -> list[Pizza]:
        """
        Retorna as pizzas de acordo com os filtros informados.

        Args:
            category: Categoria utilizada para filtrar as pizzas.
            available: Indica se devem ser retornadas pizzas disponíveis
                ou indisponíveis.
            limit: Quantidade máxima de registros retornados.
            offset: Quantidade de registros ignorados antes da consulta.

        Returns:
            Lista contendo as pizzas encontradas.
        """

        # Define explicitamente os campos retornados pela consulta.
        statement = (
            f"""
            SELECT id, name, description, category, price,
                image_name, available, created_at, updated_at
            FROM {self.table_name}
            """
        )

        filters = []

        # Adiciona o filtro de categoria quando informado.
        if category is not None:
            filters.append(f'category = "{category.value}"')

        # Adiciona o filtro booleano de disponibilidade.
        if available is not None:
            available_value = (
                'true'
                if available
                else 'false'
            )

            filters.append(f'available = {available_value}')

        # Adiciona a cláusula WHERE somente quando existem filtros.
        if filters:
            statement += (
                ' WHERE '
                + ' AND '.join(filters)
            )

        # Adiciona paginação à consulta.
        statement += (
            f' LIMIT {limit}'
            f' OFFSET {offset}'
        )

        print(statement)

        request = QueryRequest().set_statement(statement)

        pizzas = []

        # Executa a mesma QueryRequest até que todas as páginas
        # retornadas pelo Oracle NoSQL tenham sido processadas.
        while True:
            result = self.handle.query(request)

            for row in result.get_results():
                pizzas.append(self._to_model(row))

            if request.is_done():
                break

        return pizzas

    def update(self, pizza: Pizza) -> Pizza:
        """
        Atualiza uma pizza existente.

        Args:
            pizza: Modelo contendo os dados atualizados da pizza.

        Returns:
            Pizza atualizada.
        """

        row = self._to_row(pizza)

        # IF_PRESENT impede que o update crie silenciosamente uma nova
        # pizza caso o registro tenha sido removido entre a leitura
        # e a operação de atualização.
        request = (
            PutRequest()
            .set_table_name(self.table_name)
            .set_value(row)
            .set_option(PutOption.IF_PRESENT)
        )

        result = self.handle.put(request)

        if result.get_version() is None:
            raise RuntimeError(
                'Error updating pizza in Oracle NoSQL.'
            )

        return pizza

    def delete(self, pizza_id: UUID) -> None:
        """
        Remove uma pizza através de seu identificador.

        Args:
            pizza_id: Identificador UUID da pizza que será removida.

        Returns:
            None.
        """

        request = (
            DeleteRequest()
            .set_table_name(self.table_name)
            .set_key(
                {
                    'id': str(pizza_id),
                }
            )
        )

        result = self.handle.delete(request)

        # get_success() retorna False quando nenhum registro
        # correspondente à chave foi removido.
        if not result.get_success():
            raise RuntimeError(
                'Error deleting pizza from Oracle NoSQL.'
            )

    @staticmethod
    def _to_row(pizza: Pizza) -> dict:
        """
        Converte um modelo Pizza para o formato utilizado
        pelo Oracle NoSQL Database.

        Args:
            pizza: Modelo da aplicação que será convertido.

        Returns:
            Dicionário contendo os dados que serão persistidos.
        """

        return {
            'id': str(pizza.id),
            'name': pizza.name,
            'description': pizza.description,
            'category': pizza.category.value,
            'price': pizza.price,
            'image_name': pizza.image_name,
            'available': pizza.available,
            'created_at': pizza.created_at,
            'updated_at': pizza.updated_at
        }

    @staticmethod
    def _to_model(row: dict) -> Pizza:
        """
        Converte um registro do Oracle NoSQL para o modelo
        utilizado pela aplicação.

        Args:
            row: Registro retornado pelo Oracle NoSQL Database.

        Returns:
            Modelo Pizza correspondente ao registro.
        """

        return Pizza(
            id=UUID(
                row['id']
            ),
            name=row['name'],
            description=row['description'],
            category=PizzaCategory(
                row['category']
            ),
            price=row['price'],
            image_name=row['image_name'],
            available=row['available'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
