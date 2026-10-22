#
# repositories/nosql/nosql_order_repository.py
#

import re

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from borneo import (
    DeleteRequest,
    NoSQLHandle,
    PutOption,
    PutRequest,
    QueryRequest
)

from app.models.order import (
    CustomerSnapshot,
    DeliveryAddressSnapshot,
    Order,
    OrderItem,
    OrderStatus,
    PaymentStatus
)

from app.repositories.order_repository import OrderRepository


class NosqlOrderRepository(OrderRepository):
    """
    Implementa a persistência de pedidos utilizando Oracle NoSQL.

    A classe converte os modelos de domínio para a estrutura tipada criada
    pelo bootstrap e mantém os detalhes do provider isolados da camada de
    serviço.
    """

    MAX_PAGE_SIZE = 100

    def __init__(self,
                 handle: NoSQLHandle,
                 table_name: str = 'orders',
                 use_client_side_sort: bool = False) -> None:
        """
        Inicializa o repositório de pedidos.

        Args:
            handle: Handle utilizado para comunicação com o Oracle NoSQL.
            table_name: Nome da tabela que armazena os pedidos.
            use_client_side_sort: Indica se consultas administrativas devem
                ser ordenadas e paginadas localmente.

        Returns:
            None.

        Raises:
            ValueError: Quando o nome da tabela não for um identificador
                válido.
        """

        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', table_name):
            raise ValueError('Invalid Oracle NoSQL table name.')

        self.handle = handle
        self.table_name = table_name
        self.use_client_side_sort = use_client_side_sort

    def create(self, order: Order) -> Order:
        """
        Persiste um novo pedido sem sobrescrever uma chave existente.

        Args:
            order: Modelo de domínio que será persistido.

        Returns:
            Pedido persistido.

        Raises:
            RuntimeError: Quando já existir um pedido com o mesmo `id` ou a
                operação não produzir uma versão persistida.
        """

        request = (
            PutRequest()
            .set_table_name(self.table_name)
            .set_value(self._to_row(order))
            .set_option(PutOption.IF_ABSENT)
        )

        result = self.handle.put(request)

        # IF_ABSENT retorna uma operação sem versão quando a chave primária já
        # existe e, portanto, nenhum registro novo foi persistido.
        if result.get_version() is None:
            raise RuntimeError('Error creating order in Oracle NoSQL.')

        return order

    def get_by_id(self,
                  order_id: UUID,
                  user_id: UUID | None = None) -> Order | None:
        """
        Localiza um pedido diretamente pela chave primária.

        Args:
            order_id: Identificador UUID do pedido.
            user_id: Proprietário do pedido quando a consulta vier de uma
                rota de usuário. Quando ausente, usa o índice administrativo
                por identificador.

        Returns:
            Pedido encontrado ou `None` quando ele não existir.
        """

        # A tabela utiliza somente `id` como chave primária. Quando a rota de
        # usuário informa `user_id`, ele é aplicado como filtro adicional.
        user_filter = (
            f' AND user_id = "{user_id}"'
            if user_id is not None
            else ''
        )

        statement = f'''
            SELECT id, user_id, customer, delivery_address, items,
                   subtotal, delivery_fee, total, status, payment_status,
                   idempotency_key, created_at, updated_at
            FROM {self.table_name}
            WHERE id = "{order_id}"{user_filter}
            LIMIT 1
        '''

        rows = self._query(statement)
        row = rows[0] if rows else None

        return self._to_model(row) if row is not None else None

    def get_by_idempotency_key(self,
                               user_id: UUID,
                               idempotency_key: UUID) -> Order | None:
        """
        Localiza um pedido pela chave de idempotência e pelo proprietário.

        Args:
            user_id: Identificador do usuário proprietário do pedido.
            idempotency_key: Chave da tentativa de criação.

        Returns:
            Pedido encontrado ou `None` quando a chave ainda não tiver sido
            utilizada pelo usuário.
        """

        # Os valores interpolados são UUIDs já tipados pela aplicação. O
        # índice composto por usuário e idempotência atende esta consulta.
        statement = f'''
            SELECT id, user_id, customer, delivery_address, items, 
                   subtotal, delivery_fee, total, status, payment_status,
                   idempotency_key, created_at, updated_at
            FROM {self.table_name}
            WHERE idempotency_key = "{idempotency_key}"
                AND user_id = "{user_id}"
            LIMIT 1
        '''

        rows = self._query(statement)

        return self._to_model(rows[0]) if rows else None

    def get_by_user_id(self,
                       user_id: UUID,
                       limit: int = 10,
                       offset: int = 0) -> list[Order]:
        """
        Retorna uma página dos pedidos pertencentes ao usuário.

        Args:
            user_id: Identificador do usuário proprietário dos pedidos.
            limit: Quantidade máxima de registros retornados.
            offset: Quantidade de registros ignorados antes do retorno.

        Returns:
            Pedidos encontrados para o usuário.

        Raises:
            ValueError: Quando os parâmetros de paginação forem inválidos.
        """

        self._validate_pagination(limit=limit, offset=offset)

        statement = f'''
            SELECT id, user_id, customer, delivery_address, items, 
                   subtotal, delivery_fee, total, status, payment_status,
                   idempotency_key, created_at, updated_at
            FROM {self.table_name}
            WHERE user_id = "{user_id}"
        '''

        if self.use_client_side_sort:
            orders = [
                self._to_model(row)
                for row in self._query(statement)
            ]

            orders.sort(
                key=lambda order: order.created_at,
                reverse=True
            )
            
            return orders[offset:offset + limit]

        statement += (
            ' ORDER BY created_at DESC'
            f' LIMIT {limit}'
            f' OFFSET {offset}'
        )

        return [self._to_model(row) for row in self._query(statement)]

    def get_all(self,
                order_status: OrderStatus | None = None,
                payment_status: PaymentStatus | None = None,
                limit: int = 10,
                offset: int = 0) -> list[Order]:
        """
        Retorna pedidos para acompanhamento administrativo.

        Args:
            order_status: Estado do pedido utilizado como filtro opcional.
            payment_status: Estado do pagamento utilizado como filtro
                opcional.
            limit: Quantidade máxima de registros retornados.
            offset: Quantidade de registros ignorados antes do retorno.

        Returns:
            Pedidos correspondentes aos filtros informados.

        Raises:
            ValueError: Quando os parâmetros de paginação forem inválidos.
        """

        self._validate_pagination(limit=limit, offset=offset)

        filters = []

        # Os filtros são enums e, por isso, somente valores definidos pelo
        # domínio podem fazer parte da instrução.
        if order_status is not None:
            filters.append(f'status = "{order_status.value}"')

        if payment_status is not None:
            filters.append(
                f'payment_status = "{payment_status.value}"'
            )

        statement = f'''
            SELECT id, user_id, customer, delivery_address, items, 
                   subtotal, delivery_fee, total, status, payment_status,
                   idempotency_key, created_at, updated_at 
            FROM {self.table_name}
        '''

        if filters:
            statement += ' WHERE ' + ' AND '.join(filters)

        # O proxy da edição Community usada no desenvolvimento local não
        # fornece a topologia exigida pelo SDK para ordenar consultas entre
        # todos os shards. Nesse ambiente, recupera os registros antes de
        # ordenar e paginar, preservando o comportamento da API.
        if self.use_client_side_sort:
            orders = [
                self._to_model(row)
                for row in self._query(statement)
            ]
            orders.sort(
                key=lambda order: order.created_at,
                reverse=True
            )

            return orders[offset:offset + limit]

        # Em OCI, a ordenação utiliza os índices criados pelo bootstrap para
        # manter a paginação determinística e processada pelo banco de dados.
        statement += (
            ' ORDER BY created_at DESC'
            f' LIMIT {limit}'
            f' OFFSET {offset}'
        )

        return [self._to_model(row) for row in self._query(statement)]

    def get_summary(self, created_since: datetime) -> dict[str, int]:
        """
        Retorna indicadores agregados para o painel administrativo.

        Args:
            created_since: Início do período considerado no indicador de
                pedidos recebidos.

        Returns:
            Quantidades de pedidos do período e dos estados operacionais.

        Raises:
            ValueError: Quando a data recebida não possuir timezone.
        """

        if created_since.tzinfo is None:
            raise ValueError('Summary start datetime must include timezone.')

        created_since_utc = created_since.astimezone(timezone.utc)

        # O proxy Community não fornece a topologia exigida pelo SDK para
        # agregar todos os shards. No desenvolvimento, somente os campos
        # necessários são lidos e agregados localmente.
        if self.use_client_side_sort:
            rows = self._query(f'''
                SELECT status, created_at
                    FROM {self.table_name}
            ''')

            totals_by_status: dict[str, int] = {}
            orders_today = 0

            for row in rows:
                status = row['status']

                totals_by_status[status] = (
                    totals_by_status.get(status, 0) + 1
                )

                created_at = row['created_at']

                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)

                if created_at.astimezone(timezone.utc) >= created_since_utc:
                    orders_today += 1

            return {
                'orders_today': orders_today,
                'orders_preparing': totals_by_status.get('PREPARING', 0),
                'orders_ready': totals_by_status.get('READY', 0),
                'pending_orders': sum(
                    total
                    for status, total in totals_by_status.items()
                    if status not in ('DELIVERED', 'CANCELLED')
                )
            }

        created_since_value = (
            created_since_utc.isoformat(timespec='milliseconds')
            .replace('+00:00', 'Z')
        )

        status_rows = self._query(f'''
            SELECT status, count(*) AS total
                FROM {self.table_name}
            GROUP BY status
        ''')
        
        period_rows = self._query(f'''
            SELECT count(*) AS total
                FROM {self.table_name}
            WHERE created_at >= CAST(
                "{created_since_value}" AS TIMESTAMP(3)
            )
        ''')

        totals_by_status = {
            row['status']: int(row['total'])
            for row in status_rows
        }

        return {
            'orders_today': (
                int(period_rows[0]['total'])
                if period_rows
                else 0
            ),
            'orders_preparing': totals_by_status.get('PREPARING', 0),
            'orders_ready': totals_by_status.get('READY', 0),
            'pending_orders': sum(
                total
                for status, total in totals_by_status.items()
                if status not in ('DELIVERED', 'CANCELLED')
            )
        }

    def update(self, order: Order) -> Order:
        """
        Atualiza um pedido sem criar um registro ausente.

        Args:
            order: Modelo de domínio com os dados atualizados.

        Returns:
            Pedido atualizado.

        Raises:
            RuntimeError: Quando o pedido não existir ou a atualização não
                produzir uma nova versão.
        """

        request = (
            PutRequest()
            .set_table_name(self.table_name)
            .set_value(self._to_row(order))
            .set_option(PutOption.IF_PRESENT)
        )

        result = self.handle.put(request)

        if result.get_version() is None:
            raise RuntimeError('Error updating order in Oracle NoSQL.')

        return order

    def delete(self, order: Order) -> None:
        """
        Remove um pedido usando o identificador que compõe sua chave primária.

        Args:
            order: Pedido que será removido.

        Returns:
            None.

        Raises:
            RuntimeError: Quando o pedido não existir ou não for removido.
        """

        request = (
            DeleteRequest()
            .set_table_name(self.table_name)
            .set_key({
                'id': str(order.id)
            })
        )

        result = self.handle.delete(request)

        # get_success() retorna False quando nenhum registro correspondente
        # à chave foi removido.
        if not result.get_success():
            raise RuntimeError('Error deleting order in Oracle NoSQL.')

    def _query(self, statement: str) -> list[dict]:
        """
        Executa todas as páginas produzidas por uma consulta NoSQL.

        Args:
            statement: Instrução SQL for NoSQL que será executada.

        Returns:
            Registros retornados por todas as páginas da consulta.
        """

        request = QueryRequest().set_statement(statement)
        rows = []

        # A primeira chamada deve ocorrer antes de consultar is_done(), pois
        # uma requisição ainda não executada pode inicialmente parecer pronta.
        while True:
            result = self.handle.query(request)
            rows.extend(result.get_results())

            if request.is_done():
                break

        return rows

    @classmethod
    def _validate_pagination(cls, limit: int, offset: int) -> None:
        """
        Valida os limites utilizados nas consultas paginadas.

        Args:
            limit: Quantidade máxima de registros solicitada.
            offset: Quantidade de registros que será ignorada.

        Returns:
            None.

        Raises:
            ValueError: Quando `limit` ou `offset` estiver fora do intervalo
                aceito pelo repositório.
        """

        if not isinstance(limit, int) or isinstance(limit, bool):
            raise ValueError('Limit must be an integer.')

        if not 1 <= limit <= cls.MAX_PAGE_SIZE:
            raise ValueError(
                f'Limit must be between 1 and {cls.MAX_PAGE_SIZE}.'
            )

        if (
            not isinstance(offset, int)
            or isinstance(offset, bool)
            or offset < 0
        ):
            raise ValueError('Offset must be a non-negative integer.')

    @staticmethod
    def _to_row(order: Order) -> dict:
        """
        Converte um pedido para a estrutura persistida no Oracle NoSQL.

        Args:
            order: Modelo de domínio que será convertido.

        Returns:
            Registro compatível com o schema da tabela `orders`.
        """

        return {
            'id': str(order.id),
            'user_id': str(order.user_id),
            'customer': {
                'name': order.customer.name,
                'email': order.customer.email,
                'whatsapp': order.customer.whatsapp
            },
            'delivery_address': {
                'zip_code': order.delivery_address.zip_code,
                'street': order.delivery_address.street,
                'number': order.delivery_address.number,
                'complement': order.delivery_address.complement,
                'neighborhood': order.delivery_address.neighborhood,
                'city': order.delivery_address.city,
                'state': order.delivery_address.state
            },
            'items': [
                {
                    'pizza_id': str(item.pizza_id),
                    'name': item.name,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'subtotal': item.subtotal
                }
                for item in order.items
            ],
            'subtotal': order.subtotal,
            'delivery_fee': order.delivery_fee,
            'total': order.total,
            'status': order.status.value,
            'payment_status': order.payment_status.value,
            'idempotency_key': str(order.idempotency_key),
            'created_at': order.created_at,
            'updated_at': order.updated_at
        }

    @staticmethod
    def _to_model(row: dict) -> Order:
        """
        Converte um registro do Oracle NoSQL para o modelo de domínio.

        Args:
            row: Registro retornado pela tabela `orders`.

        Returns:
            Pedido reconstruído com os tipos utilizados pelo domínio.
        """

        customer = row['customer']
        address = row['delivery_address']

        return Order(
            id=UUID(row['id']),
            user_id=UUID(row['user_id']),
            customer=CustomerSnapshot(
                name=customer['name'],
                email=customer['email'],
                whatsapp=customer['whatsapp']
            ),
            delivery_address=DeliveryAddressSnapshot(
                zip_code=address['zip_code'],
                street=address['street'],
                number=address['number'],
                complement=address.get('complement'),
                neighborhood=address['neighborhood'],
                city=address['city'],
                state=address['state']
            ),
            items=[
                OrderItem(
                    pizza_id=UUID(item['pizza_id']),
                    name=item['name'],
                    quantity=int(item['quantity']),
                    unit_price=Decimal(str(item['unit_price'])),
                    subtotal=Decimal(str(item['subtotal']))
                )
                for item in row['items']
            ],
            subtotal=Decimal(str(row['subtotal'])),
            delivery_fee=Decimal(str(row['delivery_fee'])),
            total=Decimal(str(row['total'])),
            status=OrderStatus(row['status']),
            payment_status=PaymentStatus(row['payment_status']),
            idempotency_key=UUID(row['idempotency_key']),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
