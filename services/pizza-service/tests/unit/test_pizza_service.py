import pytest

from app.repositories.pizza_repository import InMemoryPizzaRepository
from app.schemas.pizza_schema import PizzaCreateRequest, PizzaUpdateRequest
from app.services.pizza_service import PizzaNotFoundError, PizzaService


def test_list_available_pizzas_returns_only_available_items():
    service = PizzaService(InMemoryPizzaRepository())
    service.create_pizza(
        PizzaCreateRequest(
            name="Margherita",
            category="tradicional",
            price=39.9,
            available=True,
        )
    )
    service.create_pizza(
        PizzaCreateRequest(
            name="Chocolate",
            category="doce",
            price=45.0,
            available=False,
        )
    )

    pizzas = service.list_available_pizzas()

    assert len(pizzas) == 1
    assert pizzas[0].name == "Margherita"


def test_update_pizza_applies_only_sent_fields():
    service = PizzaService(InMemoryPizzaRepository())
    pizza = service.create_pizza(
        PizzaCreateRequest(
            name="Margherita",
            description="Original",
            category="tradicional",
            price=39.9,
        )
    )

    updated = service.update_pizza(
        pizza.id,
        PizzaUpdateRequest(price=42.9),
    )

    assert updated.name == "Margherita"
    assert updated.description == "Original"
    assert updated.price == 42.9


def test_get_pizza_raises_when_not_found():
    service = PizzaService(InMemoryPizzaRepository())

    with pytest.raises(PizzaNotFoundError):
        service.get_pizza("pizza-missing")
