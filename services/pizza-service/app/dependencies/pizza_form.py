#
# dependencies/pizza_form.py
#

from decimal import Decimal
from typing import Annotated

from fastapi import Form

from app.models.pizza import PizzaCategory
from app.schemas.pizza_schema import PizzaCreateRequest, PizzaUpdateRequest


def get_pizza_create_form(
    name: Annotated[str, Form(min_length=1, max_length=100)],
    description: Annotated[str, Form(min_length=1, max_length=500)],
    category: Annotated[PizzaCategory, Form()],
    price: Annotated[Decimal, Form(gt=0)],
    image_name: Annotated[
        str | None,
        Form(min_length=1, max_length=255)
    ] = None,
    available: Annotated[bool, Form()] = True
) -> PizzaCreateRequest:
    """
    Converte os campos multipart da criação em um schema de entrada.

    Args:
        name: Nome da pizza, entre 1 e 100 caracteres.
        description: Descrição da pizza, entre 1 e 500 caracteres.
        category: Categoria da pizza.
        price: Preço positivo da pizza.
        image_name: Nome opcional do objeto no Object Storage. Quando não
            informado, o serviço gera um nome único.
        available: Indica se a pizza ficará disponível para pedidos.

    Returns:
        Instância validada de `PizzaCreateRequest`.
    """

    # O FastAPI já converte e valida os campos anotados com `Form` antes de
    # chamar esta dependência.
    return PizzaCreateRequest(
        name=name,
        description=description,
        category=category,
        price=price,
        image_name=image_name,
        available=available
    )


def get_pizza_update_form(
    name: Annotated[str | None, Form(min_length=1, max_length=100)] = None,
    description: Annotated[
        str | None,
        Form(min_length=1, max_length=500)
    ] = None,
    category: Annotated[PizzaCategory | None, Form()] = None,
    price: Annotated[Decimal | None, Form(gt=0, decimal_places=2)] = None,
    image_name: Annotated[
        str | None,
        Form(min_length=1, max_length=255)
    ] = None,
    available: Annotated[bool | None, Form()] = None
) -> PizzaUpdateRequest:
    """
    Converte os campos multipart da atualização em um schema parcial.

    Args:
        name: Novo nome da pizza, quando informado.
        description: Nova descrição da pizza, quando informada.
        category: Nova categoria da pizza, quando informada.
        price: Novo preço positivo da pizza, quando informado.
        image_name: Nome opcional para a nova imagem.
        available: Novo estado de disponibilidade, quando informado.

    Returns:
        Instância validada de `PizzaUpdateRequest` contendo somente os campos
        recebidos na requisição.
    """

    # Mantém os valores em um dicionário para que a atualização seja parcial.
    # Valores `None` são removidos antes da criação do schema e não alteram os
    # dados já persistidos.
    values = {
        'name': name,
        'description': description,
        'category': category,
        'price': price,
        'image_name': image_name,
        'available': available
    }

    # `exclude_unset` no schema preserva a distinção entre campo omitido e
    # campo efetivamente enviado pelo consumidor da API.
    return PizzaUpdateRequest(
        **{
            field: value
            for field, value in values.items()
            if value is not None
        }
    )
