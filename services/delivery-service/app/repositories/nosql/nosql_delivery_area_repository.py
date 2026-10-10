#
# repositories/nosql/nosql_delivery_area_repository.py
#

from decimal import Decimal
from uuid import UUID

from borneo import (
    DeleteRequest,
    GetRequest,
    NoSQLHandle,
    PutOption,
    PutRequest,
    QueryRequest
)

from app.models.delivery_area import DeliveryArea
from app.repositories.delivery_area_repository import DeliveryAreaRepository


class NosqlDeliveryAreaRepository(DeliveryAreaRepository):
    """
    Implementa a persistência das áreas de entrega utilizando OCI NoSQL.

    A implementação é responsável por converter os models de domínio em
    registros compatíveis com o OCI NoSQL e realizar as operações de
    persistência definidas por DeliveryAreaRepository.
    """

    def __init__(self,
                 handle: NoSQLHandle,
                 table_name: str = 'delivery_areas'):
        """
        Inicializa o repositório de áreas de entrega.

        Args:
            handle: Handle utilizado para comunicação com o OCI NoSQL.
            table_name: Nome da tabela utilizada para armazenar as áreas
                de entrega.
        """

        self.handle = handle
        self.table_name = table_name

    def create(self, delivery_area: DeliveryArea) -> DeliveryArea:
        """
        Cria uma nova área de entrega.

        Args:
            delivery_area: Área de entrega que será persistida.

        Returns:
            A área de entrega criada.
        """

        # Converte o model de domínio para o formato de registro esperado
        # pelo OCI NoSQL.
        row = self._to_row(delivery_area)

        # PutRequest é utilizado para inserir registros no OCI NoSQL.
        # IF_ABSENT garante que a operação somente será executada caso
        # ainda não exista um registro com a mesma chave primária.
        request = (
            PutRequest()
            .set_table_name(self.table_name)
            .set_value(row)
            .set_option(PutOption.IF_ABSENT)
        )

        self.handle.put(request)

        return delivery_area

    def get_by_id(self, delivery_area_id: UUID) -> DeliveryArea | None:
        """
        Busca uma área de entrega pelo identificador.

        Args:
            delivery_area_id: Identificador da área de entrega.

        Returns:
            A área de entrega encontrada ou None caso não exista.
        """

        # GetRequest realiza uma consulta direta utilizando a chave
        # primária da tabela, evitando a necessidade de uma query SQL.
        request = (
            GetRequest()
            .set_table_name(self.table_name)
            .set_key({
                'id': str(delivery_area_id)
            })
        )

        result = self.handle.get(request)
        row = result.get_value()

        if not row:
            return None

        return self._to_model(row)

    def get_by_zip_code(self, zip_code: str) -> DeliveryArea | None:
        """
        Busca uma área de entrega ativa que contemple o CEP informado.

        Args:
            zip_code: CEP utilizado para localizar a área de entrega.

        Returns:
            A área de entrega correspondente ao CEP ou None caso
            nenhuma área esteja disponível.
        """

        # A área correspondente ao CEP é identificada verificando se o
        # CEP está contido entre o início e o fim da faixa cadastrada.
        #
        # Os CEPs são armazenados normalizados com oito caracteres
        # numéricos, permitindo a comparação direta entre as strings.
        statement = f"""
            SELECT *
            FROM {self.table_name}
            WHERE zip_code_start <= '{zip_code}'
              AND zip_code_end >= '{zip_code}'
              AND active = true
            LIMIT 1
        """

        request = QueryRequest().set_statement(statement)

        # Uma QueryRequest pode retornar os resultados em mais de uma
        # execução. Mesmo utilizando LIMIT 1, o loop mantém o mesmo padrão
        # utilizado nas consultas ao OCI NoSQL.
        while not request.is_done():
            result = self.handle.query(request)

            rows = result.get_results()

            if rows:
                return self._to_model(rows[0])

        return None

    def get_all(self,
                active: bool | None = None,
                limit: int = 10,
                offset: int = 0) -> list[DeliveryArea]:
        """
        Retorna as áreas de entrega cadastradas.

        Args:
            active: Filtra as áreas pelo status ativo ou inativo.
            limit: Quantidade máxima de registros retornados.
            offset: Quantidade de registros ignorados antes do retorno.

        Returns:
            Lista contendo as áreas de entrega encontradas.
        """

        filters = []

        # Adiciona o filtro de status somente quando ele for informado.
        # Dessa forma, active=None retorna áreas ativas e inativas.
        if active is not None:
            active_value = 'true' if active else 'false'
            filters.append(f'active = {active_value}')

        statement = f"""
            SELECT *
            FROM {self.table_name}
        """

        # Monta dinamicamente a cláusula WHERE apenas quando existem
        # filtros informados para a consulta.
        if filters:
            statement += f"""
                WHERE {' AND '.join(filters)}
            """

        # LIMIT e OFFSET permitem que a interface administrativa realize
        # a paginação das áreas de entrega sem carregar toda a tabela.
        statement += f"""
            ORDER BY zip_code_start
            LIMIT {limit}
            OFFSET {offset}
        """

        request = QueryRequest().set_statement(statement)

        rows = []

        # O OCI NoSQL pode retornar uma consulta em múltiplos lotes.
        # O QueryRequest mantém internamente a continuação da consulta
        # até que is_done() indique que todos os resultados foram lidos.
        while not request.is_done():
            result = self.handle.query(request)
            rows.extend(result.get_results())

        return [
            self._to_model(row)
            for row in rows
        ]

    def update(self, delivery_area: DeliveryArea) -> DeliveryArea:
        """
        Atualiza uma área de entrega existente.

        Args:
            delivery_area: Área de entrega com os dados atualizados.

        Returns:
            A área de entrega atualizada.
        """

        # Converte novamente o model completo para o formato persistido
        # antes de substituir o registro existente.
        row = self._to_row(delivery_area)

        # IF_PRESENT impede que uma atualização crie acidentalmente uma
        # nova área quando a chave primária não existir na tabela.
        request = (
            PutRequest()
            .set_table_name(self.table_name)
            .set_value(row)
            .set_option(PutOption.IF_PRESENT)
        )

        self.handle.put(request)

        return delivery_area

    def delete(self, delivery_area_id: UUID) -> None:
        """
        Remove uma área de entrega.

        Args:
            delivery_area_id: Identificador da área de entrega.
        """

        # DeleteRequest remove o registro utilizando diretamente sua
        # chave primária.
        request = (
            DeleteRequest()
            .set_table_name(self.table_name)
            .set_key({
                'id': str(delivery_area_id)
            })
        )

        self.handle.delete(request)

    @staticmethod
    def _to_row(delivery_area: DeliveryArea) -> dict:
        """
        Converte uma área de entrega para um registro do OCI NoSQL.

        Args:
            delivery_area: Model de domínio que será convertido.

        Returns:
            Dicionário contendo os dados no formato utilizado pelo
            OCI NoSQL.
        """

        # UUID é convertido para string porque a coluna id da tabela
        # delivery_areas utiliza o tipo STRING no OCI NoSQL.
        return {
            'id': str(delivery_area.id),
            'name': delivery_area.name,
            'zip_code_start': delivery_area.zip_code_start,
            'zip_code_end': delivery_area.zip_code_end,
            'delivery_fee': delivery_area.delivery_fee,
            'estimated_minutes': delivery_area.estimated_minutes,
            'active': delivery_area.active,
            'created_at': delivery_area.created_at,
            'updated_at': delivery_area.updated_at
        }

    @staticmethod
    def _to_model(row: dict) -> DeliveryArea:
        """
        Converte um registro do OCI NoSQL para o model de domínio.

        Args:
            row: Registro retornado pelo OCI NoSQL.

        Returns:
            Model de domínio correspondente à área de entrega.
        """
        
        # A camada de persistência realiza a conversão dos tipos específicos
        # do banco antes de entregar a entidade para as demais camadas.
        return DeliveryArea(
            id=UUID(row['id']),
            name=row['name'],
            zip_code_start=row['zip_code_start'],
            zip_code_end=row['zip_code_end'],
            delivery_fee=Decimal(str(row['delivery_fee'])),
            estimated_minutes=row['estimated_minutes'],
            active=row['active'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )