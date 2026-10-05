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
    image_name: Annotated[str, Form(min_length=1, max_length=255)],
    available: Annotated[bool, Form()] = True
) -> PizzaCreateRequest:
    """Monta o payload de criação a partir dos campos multipart."""

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
    """Monta o payload parcial de atualização a partir do multipart."""

    values = {
        'name': name,
        'description': description,
        'category': category,
        'price': price,
        'image_name': image_name,
        'available': available
    }

    return PizzaUpdateRequest(
        **{
            field: value
            for field, value in values.items()
            if value is not None
        }
    )
