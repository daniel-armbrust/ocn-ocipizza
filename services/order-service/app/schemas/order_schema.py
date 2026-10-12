#
# schemas/order_schema.py
#

from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    model_validator
)

from app.models.order import Order, OrderStatus, PaymentStatus


class OrderCustomer(BaseModel):
    """
    Representa o snapshot do cliente incluído no pedido.

    Attributes:
        name: Nome completo do cliente.
        email: Endereço de e-mail utilizado para comunicação.
        whatsapp: Número de WhatsApp contendo somente dígitos.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        from_attributes=True
    )

    name: str = Field(min_length=3, max_length=255)
    email: EmailStr
    whatsapp: str = Field(pattern=r'^\d{11}$')


class OrderDeliveryAddress(BaseModel):
    """
    Representa o snapshot do endereço utilizado para entrega.

    Attributes:
        zip_code: CEP contendo somente oito dígitos.
        street: Logradouro do endereço.
        number: Número do imóvel.
        complement: Complemento opcional do endereço.
        neighborhood: Bairro do endereço.
        city: Cidade do endereço.
        state: Sigla da unidade federativa em letras maiúsculas.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        from_attributes=True
    )

    zip_code: str = Field(pattern=r'^\d{8}$')
    street: str = Field(min_length=1, max_length=255)
    number: str = Field(min_length=1, max_length=20)
    complement: str | None = Field(default=None, max_length=100)
    neighborhood: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(pattern=r'^[A-Z]{2}$')


class OrderItemSchema(BaseModel):
    """
    Representa uma pizza e os valores confirmados para o pedido.

    Attributes:
        pizza_id: Identificador da pizza no catálogo.
        name: Nome da pizza no momento da compra.
        quantity: Quantidade solicitada.
        unit_price: Preço unitário confirmado.
        subtotal: Resultado do preço unitário multiplicado pela quantidade.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        from_attributes=True
    )

    pizza_id: UUID
    name: str = Field(min_length=1, max_length=100)
    quantity: int = Field(ge=1, le=20)
    unit_price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    subtotal: Decimal = Field(ge=0, max_digits=12, decimal_places=2)

    @model_validator(mode='after')
    def validate_subtotal(self) -> Self:
        """
        Garante que o subtotal corresponda ao preço e à quantidade.

        Returns:
            Próprio item após a validação.

        Raises:
            ValueError: Quando o subtotal informado estiver inconsistente.
        """

        expected_subtotal = self.unit_price * self.quantity

        if self.subtotal != expected_subtotal:
            raise ValueError(
                'O subtotal do item deve corresponder ao preço unitário '
                'multiplicado pela quantidade.'
            )

        return self


class OrderCreateRequest(BaseModel):
    """
    Representa os dados necessários para criação de um pedido.

    O identificador do usuário é obtido do JWT autenticado. Identificador do
    pedido, status e datas são definidos pelo order-service e, por isso, não
    fazem parte deste contrato de entrada.

    Attributes:
        customer: Snapshot dos dados do cliente.
        delivery_address: Snapshot do endereço selecionado para entrega.
        items: Pizzas e valores confirmados no checkout.
        subtotal: Soma dos subtotais dos itens.
        delivery_fee: Taxa de entrega confirmada.
        total: Soma do subtotal com a taxa de entrega.
        idempotency_key: Chave que identifica unicamente a tentativa.
    """

    customer: OrderCustomer
    delivery_address: OrderDeliveryAddress
    items: list[OrderItemSchema] = Field(min_length=1, max_length=20)
    subtotal: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    delivery_fee: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    total: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    idempotency_key: UUID

    @model_validator(mode='after')
    def validate_totals(self) -> Self:
        """
        Valida a soma dos itens e o valor total apresentado no checkout.

        Returns:
            Próprio pedido após a validação dos valores monetários.

        Raises:
            ValueError: Quando a quantidade máxima, o subtotal ou o total
                estiverem inconsistentes.
        """

        total_quantity = sum(item.quantity for item in self.items)

        if total_quantity > 20:
            raise ValueError('O pedido pode conter no máximo 20 pizzas.')

        expected_subtotal = sum(
            (item.subtotal for item in self.items),
            start=Decimal('0.00')
        )

        if self.subtotal != expected_subtotal:
            raise ValueError(
                'O subtotal do pedido deve corresponder à soma dos itens.'
            )

        if self.total != self.subtotal + self.delivery_fee:
            raise ValueError(
                'O total do pedido deve corresponder ao subtotal somado à '
                'taxa de entrega.'
            )

        return self


class OrderStatusUpdateRequest(BaseModel):
    """
    Representa uma alteração administrativa do status do pedido.

    Attributes:
        status: Novo estado do processamento ou da entrega.
    """

    status: OrderStatus


class OrderPaymentStatusUpdateRequest(BaseModel):
    """
    Representa uma alteração do estado de pagamento do pedido.

    Attributes:
        payment_status: Novo estado informado pelo fluxo de pagamento.
    """

    payment_status: PaymentStatus


class OrderResponse(BaseModel):
    """
    Representa todos os dados de um pedido retornado pela API.

    Attributes:
        id: Identificador único do pedido.
        user_id: Identificador do usuário proprietário do pedido.
        customer: Snapshot dos dados do cliente.
        delivery_address: Snapshot do endereço de entrega.
        items: Itens e valores preservados no pedido.
        subtotal: Soma dos subtotais dos itens.
        delivery_fee: Taxa de entrega aplicada.
        total: Valor total do pedido.
        status: Estado atual do processamento e da entrega.
        payment_status: Estado atual do pagamento.
        idempotency_key: Chave que identifica a tentativa de criação.
        created_at: Data e hora de criação do pedido em UTC.
        updated_at: Data e hora da última atualização do pedido em UTC.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    customer: OrderCustomer
    delivery_address: OrderDeliveryAddress
    items: list[OrderItemSchema]
    subtotal: Decimal
    delivery_fee: Decimal
    total: Decimal
    status: OrderStatus
    payment_status: PaymentStatus
    idempotency_key: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, order: Order) -> 'OrderResponse':
        """
        Converte o modelo de domínio em um contrato de resposta da API.

        Args:
            order: Pedido retornado pela camada de domínio.

        Returns:
            Schema contendo os dados públicos e históricos do pedido.
        """

        return cls.model_validate(order)
