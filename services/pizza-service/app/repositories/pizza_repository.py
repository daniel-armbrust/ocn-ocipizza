#
# repositories/pizza_repository.py
#

from abc import ABC, abstractmethod
from uuid import UUID

from app.models.pizza import Pizza, PizzaCategory


class PizzaRepository(ABC):
    """
    Define o contrato de persistência para as pizzas.
    """

    @abstractmethod
    def create(self, pizza: Pizza) -> Pizza:
        """
        Persiste uma nova pizza.

        Args:
            pizza: Modelo contendo os dados da pizza que será persistida.

        Returns:
            Pizza persistida.
        """
        pass

    @abstractmethod
    def get_by_id(self, pizza_id: UUID) -> Pizza | None:
        """
        Retorna uma pizza através de seu identificador.

        Args:
            pizza_id: Identificador UUID da pizza.

        Returns:
            Pizza encontrada ou `None` caso não exista.
        """
        pass

    @abstractmethod
    def get_all(self,
                category: PizzaCategory | None = None,
                available: bool | None = None,
                limit: int = 10,
                offset: int = 0) -> list[Pizza]:
        """
        Retorna as pizzas cadastradas de acordo com os filtros informados.

        Args:
            category: Categoria utilizada para filtrar as pizzas.
            available: Filtra pizzas de acordo com sua disponibilidade.
            limit: Quantidade máxima de pizzas retornadas.
            offset: Quantidade de registros ignorados antes do retorno.

        Returns:
            Lista contendo as pizzas encontradas.
        """
        pass

    @abstractmethod
    def update(self, pizza: Pizza) -> Pizza:
        """
        Atualiza uma pizza existente.

        Args:
            pizza: Modelo contendo os dados atualizados da pizza.

        Returns:
            Pizza atualizada.
        """
        pass

    @abstractmethod
    def delete(self, pizza_id: UUID) -> None:
        """
        Remove uma pizza através de seu identificador.

        Args:
            pizza_id: Identificador UUID da pizza que será removida.

        Returns:
            None.
        """
        pass