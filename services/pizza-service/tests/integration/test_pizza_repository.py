from app.models.pizza_model import Pizza
from app.repositories.pizza_repository import InMemoryPizzaRepository


def test_repository_creates_updates_and_deletes_pizza():
    repository = InMemoryPizzaRepository()
    pizza = Pizza(
        name="Calabresa",
        category="tradicional",
        price=42.9,
    )

    created = repository.create(pizza)
    updated = repository.update(created.id, {"available": False})
    deleted = repository.delete(created.id)

    assert created.id == pizza.id
    assert updated is not None
    assert updated.available is False
    assert deleted is True
    assert repository.get_by_id(created.id) is None
