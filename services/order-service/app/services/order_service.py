#
# services/order_service.py
#

import logging

from uuid import NAMESPACE_URL, UUID, uuid5

from fastapi import Depends

from app.exceptions.order_exceptions import (
    OrderCreationError,
    OrderIdempotencyConflictError,
    OrderNotFoundError,
    OrderQueryError,
    OrderUpdateError,
    OrderEmailPublishError
)

from app.models.order import (
    CustomerSnapshot,
    DeliveryAddressSnapshot,
    Order,
    OrderItem,
    OrderStatus,
    PaymentStatus
)

from app.services.order_email_service import (
    OrderEmailService, 
    get_order_email_service
)

from app.repositories.order_repository import OrderRepository
from app.dependencies.database import get_order_repository

from app.repositories.unit_of_work import UnitOfWork
from app.dependencies.database import get_unit_of_work

from app.schemas.order_schema import OrderCreateRequest

from app.utils.utils import now_utc


class OrderService:
    """
    Implementa os casos de uso relacionados aos pedidos.

    A camada de serviço constrói o domínio e controla a unidade de trabalho
    sem conhecer o provider utilizado para persistência.
    """

    def __init__(self,
                 order_repository: OrderRepository,
                 unit_of_work: UnitOfWork,
                 order_email_service: OrderEmailService) -> None:
        """
        Inicializa o serviço de pedidos.

        Args:
            order_repository: Repositório utilizado para consultar e
                persistir pedidos.
            unit_of_work: Unidade de trabalho responsável por confirmar ou
                reverter alterações.
            order_email_service: Serviço responsável pela publicação das 
                notificações por e-mail relacionadas aos pedidos.

        Returns:
            None.
        """

        self.order_repository = order_repository
        self.unit_of_work = unit_of_work
        self.order_email_service = order_email_service

    def get_by_user_id(self,
                       user_id: UUID,
                       limit: int = 10,
                       offset: int = 0) -> list[Order]:
        """
        Retorna uma página dos pedidos pertencentes ao usuário.

        Args:
            user_id: Identificador do usuário autenticado.
            limit: Quantidade máxima de pedidos retornados.
            offset: Quantidade de pedidos ignorados antes do retorno.

        Returns:
            Pedidos encontrados, do mais recente para o mais antigo.

        Raises:
            OrderQueryError: Quando o repositório não conseguir concluir a
                consulta.
        """

        try:
            return self.order_repository.get_by_user_id(
                user_id=user_id,
                limit=limit,
                offset=offset
            )
        except Exception as ex:
            raise OrderQueryError('Error retrieving orders.') from ex

    def get_by_id(self, user_id: UUID, order_id: UUID) -> Order:
        """
        Retorna um pedido pertencente ao usuário autenticado.

        A ausência do pedido e a tentativa de consultar um pedido de outro
        usuário produzem a mesma resposta para não revelar sua existência.

        Args:
            user_id: Identificador do usuário autenticado.
            order_id: Identificador do pedido solicitado.

        Returns:
            Pedido encontrado e pertencente ao usuário.

        Raises:
            OrderNotFoundError: Quando o pedido não existir ou pertencer a
                outro usuário.
            OrderQueryError: Quando o repositório não conseguir concluir a
                consulta.
        """

        try:
            order = self.order_repository.get_by_id(
                order_id=order_id,
                user_id=user_id
            )
        except Exception as ex:
            raise OrderQueryError('Error retrieving order.') from ex

        # A validação do proprietário impede que um UUID conhecido seja usado
        # para consultar os dados históricos do pedido de outro usuário.
        if order is None or order.user_id != user_id:
            raise OrderNotFoundError('Order not found.')

        return order

    def get_all(self,
                order_status: OrderStatus | None = None,
                payment_status: PaymentStatus | None = None,
                limit: int = 10,
                offset: int = 0) -> list[Order]:
        """
        Retorna uma página de pedidos para acompanhamento administrativo.

        Args:
            order_status: Estado do pedido utilizado como filtro opcional.
            payment_status: Estado do pagamento utilizado como filtro
                opcional.
            limit: Quantidade máxima de pedidos retornados.
            offset: Quantidade de pedidos ignorados antes do retorno.

        Returns:
            Pedidos correspondentes aos filtros informados.

        Raises:
            OrderQueryError: Quando o repositório não conseguir concluir a
                consulta.
        """

        try:
            return self.order_repository.get_all(
                order_status=order_status,
                payment_status=payment_status,
                limit=limit,
                offset=offset
            )
        except Exception as ex:
            raise OrderQueryError('Error retrieving orders.') from ex

    def get_by_id_for_admin(self, order_id: UUID) -> Order:
        """
        Retorna um pedido para acompanhamento administrativo.

        Diferentemente da consulta do usuário, esta operação não restringe o
        pedido por proprietário, pois a autorização administrativa já foi
        validada pela dependência da rota.

        Args:
            order_id: Identificador do pedido solicitado.

        Returns:
            Pedido encontrado.

        Raises:
            OrderNotFoundError: Quando o pedido não existir.
            OrderQueryError: Quando o repositório não conseguir concluir a
                consulta.
        """

        try:
            order = self.order_repository.get_by_id(order_id=order_id)
        except Exception as ex:
            raise OrderQueryError('Error retrieving order.') from ex

        if order is None:
            raise OrderNotFoundError('Order not found.')

        return order

    def update_status_for_admin(self,
                                order_id: UUID,
                                order_status: OrderStatus) -> Order:
        """
        Atualiza o estado de processamento ou entrega de um pedido.

        Args:
            order_id: Identificador do pedido que será atualizado.
            order_status: Novo estado do pedido.

        Returns:
            Pedido com o estado e a data de atualização modificados.

        Raises:
            OrderNotFoundError: Quando o pedido não existir.
            OrderQueryError: Quando não for possível consultar o pedido.
            OrderUpdateError: Quando não for possível persistir a alteração.
        """

        order = self.get_by_id_for_admin(order_id=order_id)
        order.status = order_status
        order.updated_at = now_utc()

        try:
            updated_order = self.order_repository.update(order)
            self.unit_of_work.commit()
            return updated_order
        except Exception as ex:
            self.unit_of_work.rollback()
            raise OrderUpdateError('Error updating order status.') from ex

    def create(self,
               user_id: UUID,
               payload: OrderCreateRequest) -> Order:
        """
        Cria um pedido de maneira idempotente para o usuário autenticado.

        A mesma chave acompanhada do mesmo conteúdo retorna o pedido já
        persistido. A reutilização da chave com conteúdo diferente é rejeitada
        para evitar associar uma tentativa a outro pedido.

        Args:
            user_id: Identificador do usuário autenticado.
            payload: Snapshots, itens, valores e chave de idempotência.

        Returns:
            Pedido criado ou pedido equivalente previamente persistido.

        Raises:
            OrderIdempotencyConflictError: Quando a chave já estiver associada
                a dados diferentes.
            OrderCreationError: Quando a consulta ou a persistência falhar.
        """

        try:
            existing_order = self.order_repository.get_by_idempotency_key(
                user_id=user_id,
                idempotency_key=payload.idempotency_key
            )
        except Exception as ex:
            raise OrderCreationError(
                'Error checking order idempotency.'
            ) from ex

        if existing_order is not None:
            return self._resolve_idempotent_order(
                order=existing_order,
                user_id=user_id,
                payload=payload
            )

        now = now_utc()

        # Derivar o identificador da combinação usuário + idempotência faz
        # requisições concorrentes disputarem a mesma chave primária. Dessa
        # forma, o IF_ABSENT do repositório NoSQL permite apenas uma criação.
        order_id = uuid5(
            NAMESPACE_URL,
            f'ocipizza:order:{user_id}:{payload.idempotency_key}'
        )

        # O POST /orders é chamado somente após a aprovação do pagamento.
        # Por isso, o pedido nasce como recebido e com pagamento confirmado.
        order = Order(
            id=order_id,
            user_id=user_id,
            customer=CustomerSnapshot(
                name=payload.customer.name,
                email=str(payload.customer.email),
                whatsapp=payload.customer.whatsapp
            ),
            delivery_address=DeliveryAddressSnapshot(
                zip_code=payload.delivery_address.zip_code,
                street=payload.delivery_address.street,
                number=payload.delivery_address.number,
                complement=payload.delivery_address.complement,
                neighborhood=payload.delivery_address.neighborhood,
                city=payload.delivery_address.city,
                state=payload.delivery_address.state
            ),
            items=[
                OrderItem(
                    pizza_id=item.pizza_id,
                    name=item.name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    subtotal=item.subtotal
                )
                for item in payload.items
            ],
            subtotal=payload.subtotal,
            delivery_fee=payload.delivery_fee,
            total=payload.total,
            status=OrderStatus.RECEIVED,
            payment_status=PaymentStatus.PAID,
            idempotency_key=payload.idempotency_key,
            created_at=now,
            updated_at=now
        )

        try:
            created_order = self.order_repository.create(order)
            self.unit_of_work.commit()
        except Exception as ex:
            self.unit_of_work.rollback()

            # Outra requisição pode ter persistido a mesma chave primária entre
            # a primeira consulta e o create. A leitura direta pelo ID evita
            # depender da atualização assíncrona do índice secundário.
            try:
                concurrent_order = self.order_repository.get_by_id(
                    order_id=order.id,
                    user_id=user_id
                )
            except Exception:
                raise OrderCreationError('Error creating order.') from ex

            if concurrent_order is not None:
                # Retorna o pedido já criado pela requisição concorrente sem
                # publicar uma nova notificação, evitando e-mails duplicados.
                return self._resolve_idempotent_order(
                    order=concurrent_order,
                    user_id=user_id,
                    payload=payload
                )

            raise OrderCreationError('Error creating order.') from ex

        # Publica a notificação somente depois que o pedido foi persistido
        # e sua transação confirmada com sucesso.
        try:
            self.order_email_service.send_order_received(created_order)
        except OrderEmailPublishError:
            logging.exception(
                'Não foi possível publicar a notificação do pedido %s.',
                created_order.id
            )

        return created_order

    @staticmethod
    def _resolve_idempotent_order(order: Order,
                                  user_id: UUID,
                                  payload: OrderCreateRequest) -> Order:
        """
        Confirma que o pedido persistido representa a mesma tentativa.

        Args:
            order: Pedido previamente associado à chave de idempotência.
            user_id: Identificador do usuário autenticado.
            payload: Conteúdo da tentativa atual.

        Returns:
            Pedido persistido quando todos os dados coincidirem.

        Raises:
            OrderIdempotencyConflictError: Quando a mesma chave estiver
                associada a um conteúdo diferente.
        """

        persisted_payload = OrderCreateRequest.model_validate({
            'customer': order.customer,
            'delivery_address': order.delivery_address,
            'items': order.items,
            'subtotal': order.subtotal,
            'delivery_fee': order.delivery_fee,
            'total': order.total,
            'idempotency_key': order.idempotency_key
        })

        if order.user_id != user_id or persisted_payload != payload:
            raise OrderIdempotencyConflictError(
                'Idempotency key is already associated with another order.'
            )

        return order


def get_order_service(
    order_repository: OrderRepository = Depends(get_order_repository),
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
    order_email_service: OrderEmailService = Depends(get_order_email_service)
) -> OrderService:
    """
    Fornece o serviço configurado para os casos de uso de pedidos.

    Args:
        order_repository: Repositório selecionado pelo provider configurado.
        unit_of_work: Unidade de trabalho correspondente ao mesmo provider.

    Returns:
        Serviço de pedidos pronto para utilização pelas rotas.
    """

    return OrderService(
        order_repository=order_repository,
        unit_of_work=unit_of_work,
        order_email_service=order_email_service
    )
