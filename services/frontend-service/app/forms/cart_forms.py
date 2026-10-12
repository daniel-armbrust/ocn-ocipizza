#
# forms/cart_forms.py
#

from wtforms import (
    DecimalField,
    FieldList,
    Form,
    FormField,
    IntegerField,
    StringField
)
from wtforms.validators import (
    DataRequired,
    InputRequired,
    Length,
    NumberRange,
    UUID,
    ValidationError
)


MAX_PIZZAS_PER_CHECKOUT = 20


class CartItemForm(Form):
    """
    Define e valida um item enviado pelo formulário do carrinho.

    O formulário recebe somente o identificador e a quantidade. Nome, preço e
    demais informações da pizza devem ser obtidos novamente no backend.
    """

    pizza_id = StringField(
        'Pizza',
        validators=[
            DataRequired(message='Informe a pizza.'),
            UUID(message='Informe um identificador de pizza válido.')
        ]
    )

    quantity = IntegerField(
        'Quantidade',
        validators=[
            InputRequired(message='Informe a quantidade da pizza.'),
            NumberRange(
                min=1,
                max=MAX_PIZZAS_PER_CHECKOUT,
                message=(
                    'A quantidade de cada pizza deve estar entre 1 e '
                    f'{MAX_PIZZAS_PER_CHECKOUT}.'
                )
            )
        ]
    )


class CartCheckoutForm(Form):
    """
    Define e valida os itens submetidos durante a finalização do carrinho.

    Os nomes esperados para os campos seguem o padrão do `FieldList`, como
    `items-0-pizza_id`, `items-0-quantity`, `items-1-pizza_id` e
    `items-1-quantity`.
    """

    items = FieldList(
        FormField(CartItemForm),
        min_entries=1,
        max_entries=MAX_PIZZAS_PER_CHECKOUT,
        validators=[
            DataRequired(message='Adicione pelo menos uma pizza ao carrinho.')
        ]
    )

    def validate_items(self, field: FieldList) -> None:
        """
        Valida a quantidade total de pizzas submetidas no checkout.

        Args:
            field: Lista de itens e quantidades recebida do carrinho.

        Returns:
            None.

        Raises:
            ValidationError: Quando a soma das quantidades ultrapassar o
                limite permitido por solicitação.
        """

        total_quantity = sum(
            entry.form.quantity.data or 0
            for entry in field.entries
        )

        if total_quantity > MAX_PIZZAS_PER_CHECKOUT:
            raise ValidationError(
                'O pedido pode conter no máximo '
                f'{MAX_PIZZAS_PER_CHECKOUT} pizzas.'
            )


class CartCheckoutConfirmationItemForm(CartItemForm):
    """
    Define os dados de um item apresentados na tela de checkout.
    """

    unit_price = DecimalField(
        'Preço unitário',
        places=2,
        validators=[
            InputRequired(message='Informe o preço apresentado da pizza.'),
            NumberRange(
                min=0,
                message='O preço apresentado da pizza é inválido.'
            )
        ]
    )


class CartCheckoutConfirmationForm(CartCheckoutForm):
    """
    Valida os dados submetidos para confirmação do checkout.

    Os valores monetários representam apenas o estado apresentado ao usuário
    e serão comparados com os dados atuais obtidos dos microserviços.
    """

    items = FieldList(
        FormField(CartCheckoutConfirmationItemForm),
        min_entries=1,
        max_entries=MAX_PIZZAS_PER_CHECKOUT,
        validators=[
            DataRequired(message='Adicione pelo menos uma pizza ao carrinho.')
        ]
    )

    address_id = StringField(
        'Endereço',
        validators=[
            DataRequired(message='Informe o endereço de entrega.'),
            UUID(message='Informe um identificador de endereço válido.')
        ]
    )

    subtotal = DecimalField(
        'Subtotal',
        places=2,
        validators=[
            InputRequired(message='Informe o subtotal apresentado.'),
            NumberRange(min=0, message='O subtotal apresentado é inválido.')
        ]
    )

    delivery_fee = DecimalField(
        'Taxa de entrega',
        places=2,
        validators=[
            InputRequired(message='Informe a taxa de entrega apresentada.'),
            NumberRange(
                min=0,
                message='A taxa de entrega apresentada é inválida.'
            )
        ]
    )

    total = DecimalField(
        'Total',
        places=2,
        validators=[
            InputRequired(message='Informe o total apresentado.'),
            NumberRange(min=0, message='O total apresentado é inválido.')
        ]
    )

    payment_token = StringField(
        'Token de pagamento',
        validators=[
            DataRequired(message='Informe o token do gateway de pagamento.'),
            Length(
                max=4096,
                message='O token do gateway de pagamento é inválido.'
            )
        ]
    )

    idempotency_key = StringField(
        'Chave de idempotência',
        validators=[
            DataRequired(message='Informe a chave de idempotência.'),
            UUID(message='Informe uma chave de idempotência válida.')
        ]
    )
