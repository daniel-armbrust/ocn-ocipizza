from __future__ import annotations

from typing import List

from app.models.pizza_model import Pizza
from app.repositories.pizza_repository import PizzaRepository
from app.schemas.pizza_schema import PizzaCreateRequest, PizzaUpdateRequest


class PizzaNotFoundError(Exception):
    """Erro lançado quando uma pizza não é encontrada."""

    pass


class PizzaService:
    """Implementa os casos de uso do domínio de catálogo de pizzas."""

    def __init__(self, repository: PizzaRepository) -> None:
        """
        Inicializa o serviço de catálogo de pizzas.

        Args:
            repository: Repositório usado para persistir e consultar pizzas.
        """

        self.repository = repository

    def list_available_pizzas(self) -> List[Pizza]:
        """
        Lista pizzas disponíveis para apresentação no catálogo.

        Returns:
            Lista de pizzas marcadas como disponíveis.
        """

        return self.repository.list_available()

    def get_pizza(self, pizza_id: int) -> Pizza:
        """
        Retorna uma pizza pelo identificador.

        Args:
            pizza_id: Identificador da pizza consultada.

        Returns:
            Pizza encontrada no catálogo.

        Raises:
            PizzaNotFoundError: Se nenhuma pizza existir para o identificador.
        """

        pizza = self.repository.get_by_id(pizza_id)

        if pizza is None:
            raise PizzaNotFoundError

        return pizza

    def create_pizza(self, payload: PizzaCreateRequest) -> Pizza:
        """
        Cria uma pizza a partir do contrato de entrada da API.

        Args:
            payload: Dados validados para criação da pizza.

        Returns:
            Pizza criada no catálogo.
        """

        pizza = Pizza(**payload.model_dump())

        return self.repository.create(pizza)

    def update_pizza(self, pizza_id: int, payload: PizzaUpdateRequest) -> Pizza:
        """
        Atualiza parcialmente uma pizza existente.

        Args:
            pizza_id: Identificador da pizza que será atualizada.
            payload: Campos validados enviados para atualização.

        Returns:
            Pizza atualizada.

        Raises:
            PizzaNotFoundError: Se a pizza informada não existir.
        """

        values = payload.model_dump(exclude_unset=True)
        pizza = self.repository.update(pizza_id, values)

        if pizza is None:
            raise PizzaNotFoundError

        return pizza

    def delete_pizza(self, pizza_id: int) -> None:
        """
        Remove uma pizza existente do catálogo.

        Args:
            pizza_id: Identificador da pizza que será removida.

        Raises:
            PizzaNotFoundError: Se a pizza informada não existir.
        """

        deleted = self.repository.delete(pizza_id)

        if not deleted:
            raise PizzaNotFoundError
