#
# repositories/sqlalchemy/sqlalchemy_session_repository.py
#

from sqlalchemy.orm import Session


class SqlAlchemySessionRepository:
    """
    Implementa a persistência relacional das sessões do frontend-service.
    """

    def __init__(self, session: Session) -> None:
        """
        Inicializa o repositório com a sessão compartilhada da requisição.

        Args:
            session: Sessão SQLAlchemy utilizada para persistência.

        Returns:
            None.
        """

        self.session = session
