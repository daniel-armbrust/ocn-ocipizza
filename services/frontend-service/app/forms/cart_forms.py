#
# forms/cart_forms.py
#

from wtforms import FieldList, Form, FormField, IntegerField, StringField
from wtforms.validators import (
    DataRequired,
    InputRequired,
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
