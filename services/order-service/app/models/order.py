#
# models/order.py
#

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID


class OrderStatus(str, Enum):
    """
    Estados possíveis durante o processamento e a entrega de um pedido.
    """

    RECEIVED = 'RECEIVED'
    PREPARING = 'PREPARING'
    READY = 'READY'
    OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY'
    DELIVERED = 'DELIVERED'
    CANCELLED = 'CANCELLED'


class PaymentStatus(str, Enum):
    """
    Estados possíveis do pagamento associado a um pedido.
    """

    PENDING = 'PENDING'
    PAID = 'PAID'
    FAILED = 'FAILED'
    REFUNDED = 'REFUNDED'
    CANCELLED = 'CANCELLED'


@dataclass
class CustomerSnapshot:
    """
    Representa os dados do cliente preservados no momento do pedido.

    Attributes:
        name: Nome completo apresentado no pedido.
        email: Endereço de e-mail utilizado para comunicação.
        whatsapp: Número de WhatsApp utilizado para contato.
    """

    name: str
    email: str
    whatsapp: str


@dataclass
class DeliveryAddressSnapshot:
    """
    Representa o endereço de entrega preservado no momento do pedido.

    Attributes:
        zip_code: CEP do endereço de entrega.
        street: Logradouro do endereço.
        number: Número do imóvel.
        complement: Complemento opcional do endereço.
        neighborhood: Bairro do endereço.
        city: Cidade do endereço.
        state: Sigla da unidade federativa.
    """

    zip_code: str
    street: str
    number: str
    complement: str | None
    neighborhood: str
    city: str
    state: str


@dataclass
class OrderItem:
    """
    Representa o snapshot de uma pizza incluída no pedido.

    Attributes:
        pizza_id: Identificador da pizza no catálogo.
        name: Nome da pizza no momento da compra.
        quantity: Quantidade solicitada.
        unit_price: Preço unitário aplicado ao pedido.
        subtotal: Resultado do preço unitário multiplicado pela quantidade.
    """

    pizza_id: UUID
    name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


@dataclass
class Order:
    """
    Representa um pedido persistido pelo order-service.

    Os dados do cliente, endereço e pizzas são snapshots. Dessa forma,
    alterações posteriores nos serviços de origem não modificam o histórico
    do pedido que foi efetivamente realizado.

    Attributes:
        id: Identificador único do pedido.
        user_id: Identificador do usuário proprietário do pedido.
        customer: Snapshot dos dados do cliente.
        delivery_address: Snapshot do endereço selecionado para entrega.
        items: Pizzas, quantidades e preços confirmados no pedido.
        subtotal: Soma dos subtotais dos itens.
        delivery_fee: Taxa de entrega aplicada.
        total: Soma do subtotal com a taxa de entrega.
        status: Estado atual do processamento e da entrega.
        payment_status: Estado atual do pagamento.
        idempotency_key: Chave utilizada para impedir pedidos duplicados.
        created_at: Data e hora de criação do pedido em UTC.
        updated_at: Data e hora da última atualização do pedido em UTC.
    """

    id: UUID
    user_id: UUID
    customer: CustomerSnapshot
    delivery_address: DeliveryAddressSnapshot
    items: list[OrderItem]
    subtotal: Decimal
    delivery_fee: Decimal
    total: Decimal
    status: OrderStatus
    payment_status: PaymentStatus
    idempotency_key: UUID
    created_at: datetime
    updated_at: datetime
