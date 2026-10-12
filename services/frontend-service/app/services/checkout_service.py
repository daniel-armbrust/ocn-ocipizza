#
# services/checkout_service.py
#

import asyncio

from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import UUID

from fastapi import Depends

from app.clients.delivery_client import DeliveryClient, get_delivery_client
from app.clients.pizza_client import PizzaClient, get_pizza_client
from app.clients.user_client import UserClient, get_user_client

from app.exceptions.checkout_exceptions import CheckoutChangedError


class CheckoutService:
    """
    Prepara e revalida os dados necessários para finalizar um pedido.
    """

    def __init__(self,
                 pizza_client: PizzaClient,
                 user_client: UserClient,
                 delivery_client: DeliveryClient) -> None:
        """
        Inicializa o serviço com os clientes dos microserviços envolvidos.

        Args:
            pizza_client: Cliente utilizado para consultar pizzas.
            user_client: Cliente utilizado para consultar endereços.
            delivery_client: Cliente utilizado para cotar a entrega.

        Returns:
            None.
        """

        self.pizza_client = pizza_client
        self.user_client = user_client
        self.delivery_client = delivery_client

    async def prepare_checkout(self,
                               access_token: str,
                               items: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Prepara os dados que serão apresentados na página de checkout.

        Args:
            access_token: Token JWT do usuário autenticado.
            items: Identificadores e quantidades das pizzas solicitadas.

        Returns:
            Checkout composto para apresentação e posterior confirmação.

        Raises:
            httpx.HTTPStatusError: Caso um microserviço responda com erro.
            httpx.RequestError: Caso ocorra uma falha de comunicação.
        """

        return await self._compose_checkout(
            access_token=access_token,
            items=items
        )

    async def confirm_checkout(self,
                               access_token: str,
                               submitted_checkout: dict[str, Any],
                               payment_token: str,
                               idempotency_key: str) -> dict[str, Any]:
        """
        Revalida o checkout e prepara sua futura criação no order-service.

        Args:
            access_token: Token JWT do usuário autenticado.
            submitted_checkout: Itens, endereço e valores recebidos do HTML.
            payment_token: Token opaco produzido pelo provedor de pagamento.
            idempotency_key: Chave UUID que identifica unicamente a tentativa
                de criação do pedido.

        Returns:
            Checkout atual revalidado e pronto para ser enviado ao
            order-service.

        Raises:
            CheckoutChangedError: Quando os dados atuais forem diferentes dos
                apresentados anteriormente ao usuário.
            ValueError: Quando o token de pagamento não for informado ou a
                chave de idempotência não possuir um UUID válido.
            httpx.HTTPStatusError: Caso um microserviço responda com erro.
            httpx.RequestError: Caso ocorra uma falha de comunicação.
        """

        if not isinstance(payment_token, str) or not payment_token.strip():
            raise ValueError('O token de pagamento deve ser informado.')

        try:
            UUID(str(idempotency_key))
        except (TypeError, ValueError, AttributeError) as ex:
            raise ValueError(
                'A chave de idempotência deve ser um UUID válido.'
            ) from ex

        try:
            submitted_items = submitted_checkout['items']
        except (KeyError, TypeError) as ex:
            raise CheckoutChangedError() from ex

        current_checkout = await self._compose_checkout(
            access_token=access_token,
            items=submitted_items
        )

        self._ensure_checkout_unchanged(
            submitted_checkout=submitted_checkout,
            current_checkout=current_checkout
        )

        # TODO: Enviar `current_checkout`, `payment_token` e `idempotency_key`
        # ao order-service.
        return current_checkout

    async def _compose_checkout(self,
                                access_token: str,
                                items: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Compõe os dados completos do checkout com informações atuais.

        Os itens recebidos contêm somente identificadores e quantidades. O
        método consulta os microserviços e constrói `checkout_items` com os
        dados oficiais das pizzas, incluindo preço, disponibilidade e
        subtotal. Em seguida, acrescenta endereço, cotação de entrega e os
        totais necessários para apresentar e posteriormente revalidar o
        checkout.

        Args:
            access_token: Token JWT do usuário autenticado.
            items: Identificadores e quantidades das pizzas solicitadas.

        Returns:
            Checkout composto com `checkout_items`, endereço, entrega,
            disponibilidade e valores calculados.

        Raises:
            httpx.HTTPStatusError: Caso um microserviço responda com erro.
            httpx.RequestError: Caso ocorra uma falha de comunicação.
        """

        # Pizzas e endereços são consultados em paralelo porque uma operação
        # não depende do resultado da outra.
        pizzas, addresses = await asyncio.gather(
            asyncio.gather(*[
                self.pizza_client.get_by_id(item['pizza_id'])
                for item in items
            ]),

            self.user_client.get_addresses(access_token=access_token)
        )

        checkout_items = []
        subtotal = Decimal('0.00')

        # Preços enviados pelo navegador são ignorados. Cada subtotal utiliza
        # exclusivamente o preço atual retornado pelo pizza-service.
        for submitted_item, pizza in zip(items, pizzas):
            quantity = int(submitted_item['quantity'])
            unit_price = Decimal(str(pizza['price']))
            item_subtotal = unit_price * quantity

            checkout_items.append({
                'pizza_id': pizza['id'],
                'name': pizza['name'],
                'image_url': pizza['image_url'],
                'available': pizza['available'],
                'quantity': quantity,
                'unit_price': unit_price,
                'subtotal': item_subtotal
            })

            subtotal += item_subtotal

        unavailable_items = [
            item for item in checkout_items if not item['available']
        ]

        # O checkout não escolhe outro endereço silenciosamente quando o
        # usuário não possui um endereço principal.
        address = next(
            (address for address in addresses if address.get('is_default')),
            None
        )
        
        # Evita uma cotação sem destino ou para um carrinho que já esteja
        # impedido de prosseguir por indisponibilidade de alguma pizza.
        delivery_quote = None
        
        if address and not unavailable_items:
            delivery_quote = await self.delivery_client.get_quote(
                access_token=access_token,
                zip_code=address['zip_code']
            )

        # Uma resposta HTTP bem-sucedida do delivery-service não garante que
        # o CEP seja atendido. `delivery_available` representa a elegibilidade
        # informada explicitamente pelo campo `available` da cotação.
        delivery_available = bool(
            delivery_quote and delivery_quote.get('available')
        )

        # A taxa participa do total somente quando a entrega estiver
        # disponível. O valor zero nos demais casos permite montar a tela sem
        # considerar uma taxa inexistente como parte do pedido.
        delivery_fee = (
            Decimal(str(delivery_quote['delivery_fee']))
            if delivery_available
            else Decimal('0.00')
        )

        # O checkout somente pode prosseguir para a confirmação quando existe
        # um endereço principal, todas as pizzas estão disponíveis e o CEP é
        # elegível para entrega.
        checkout_ready = bool(
            address and not unavailable_items and delivery_available
        )

        return {
            'items': checkout_items,
            'address': address,
            'has_addresses': bool(addresses),
            'delivery_quote': delivery_quote,
            'delivery_fee': delivery_fee,
            'subtotal': subtotal,
            'total': subtotal + delivery_fee,
            'unavailable_items': unavailable_items,
            'checkout_ready': checkout_ready
        }

    @staticmethod
    def _ensure_checkout_unchanged(
        submitted_checkout: dict[str, Any],
        current_checkout: dict[str, Any]
    ) -> None:
        """
        Garante que o checkout apresentado ainda possui os mesmos valores.

        Args:
            submitted_checkout: Estado recebido do formulário HTML.
            current_checkout: Estado recalculado com dados atuais das APIs.

        Returns:
            None.

        Raises:
            CheckoutChangedError: Quando algum dado estiver ausente, for
                inválido ou estiver diferente do checkout atual.
        """

        try:
            submitted_items = sorted(
                (
                    str(item['pizza_id']),
                    int(item['quantity']),
                    Decimal(str(item['unit_price']))
                )
                for item in submitted_checkout['items']
            )
            
            current_items = sorted(
                (
                    str(item['pizza_id']),
                    int(item['quantity']),
                    Decimal(str(item['unit_price']))
                )
                for item in current_checkout['items']
            )

            submitted_address_id = str(submitted_checkout['address_id'])
            current_address_id = str(current_checkout['address']['id'])

            unchanged = all((
                current_checkout['checkout_ready'],
                submitted_items == current_items,
                submitted_address_id == current_address_id,
                Decimal(str(submitted_checkout['subtotal']))
                    == current_checkout['subtotal'],
                Decimal(str(submitted_checkout['delivery_fee']))
                    == current_checkout['delivery_fee'],
                Decimal(str(submitted_checkout['total']))
                    == current_checkout['total']
            ))
        except (InvalidOperation, KeyError, TypeError, ValueError) as ex:
            # Dados ausentes ou valores monetários inválidos representam um
            # checkout alterado e nunca devem seguir para o order-service.
            raise CheckoutChangedError() from ex

        if not unchanged:
            raise CheckoutChangedError()


def get_checkout_service(
    pizza_client: PizzaClient = Depends(get_pizza_client),
    user_client: UserClient = Depends(get_user_client),
    delivery_client: DeliveryClient = Depends(get_delivery_client)
) -> CheckoutService:
    """
    Fornece o serviço utilizado para preparar e confirmar o checkout.

    Args:
        pizza_client: Cliente configurado do pizza-service.
        user_client: Cliente configurado do user-service.
        delivery_client: Cliente configurado do delivery-service.

    Returns:
        Instância configurada de `CheckoutService`.
    """

    return CheckoutService(
        pizza_client=pizza_client,
        user_client=user_client,
        delivery_client=delivery_client
    )
