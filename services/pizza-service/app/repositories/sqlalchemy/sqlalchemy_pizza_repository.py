#
# repositories/sqlalchemy/sqlalchemy_pizza_repository.py
#

from sqlalchemy.orm import Session

from app.repositories.pizza_repository import PizzaRepository

class SqlAlchemyPizzaRepository(PizzaRepository):
    def __init__(self, session: Session) -> None:
        """
        Inicializa o repositório.

        Args:
            session: Sessão SQLAlchemy utilizada para persistência.
        """

        self.session = session