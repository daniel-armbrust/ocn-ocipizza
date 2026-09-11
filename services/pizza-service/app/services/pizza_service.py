from __future__ import annotations

from typing import List

from app.models.pizza_model import Pizza
from app.repositories.pizza_repository import PizzaRepository
from app.schemas.pizza_schema import PizzaCreateRequest, PizzaUpdateRequest


class PizzaNotFoundError(Exception):
    pass


class PizzaService:
    def __init__(self, repository: PizzaRepository) -> None:
        self.repository = repository

    def list_available_pizzas(self) -> List[Pizza]:
        return self.repository.list_available()

    def get_pizza(self, pizza_id: int) -> Pizza:
        pizza = self.repository.get_by_id(pizza_id)

        if pizza is None:
            raise PizzaNotFoundError

        return pizza

    def create_pizza(self, payload: PizzaCreateRequest) -> Pizza:
        pizza = Pizza(**payload.model_dump())

        return self.repository.create(pizza)

    def update_pizza(self, pizza_id: int, payload: PizzaUpdateRequest) -> Pizza:
        values = payload.model_dump(exclude_unset=True)
        pizza = self.repository.update(pizza_id, values)

        if pizza is None:
            raise PizzaNotFoundError

        return pizza

    def delete_pizza(self, pizza_id: int) -> None:
        deleted = self.repository.delete(pizza_id)

        if not deleted:
            raise PizzaNotFoundError
