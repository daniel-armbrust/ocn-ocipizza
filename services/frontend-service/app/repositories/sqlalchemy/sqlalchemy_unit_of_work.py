#
# repositories/sqlalchemy/sqlalchemy_unit_of_work.py
#


from sqlalchemy.orm import Session

from app.repositories.unit_of_work import UnitOfWork


class SqlAlchemyUnitOfWork(UnitOfWork):
    """
    Implementação de UnitOfWork utilizando uma sessão SQLAlchemy.

    Responsável por confirmar ou reverter a transação associada à 
    sessão utilizada pelos repositórios durante o caso de uso.
    """

    def __init__(self, session: Session) -> None:
        """
        Inicializa a unidade de trabalho.

        Args:
            session: Sessão SQLAlchemy utilizada para controle da transação.
        """
        self.session = session

    def commit(self) -> None:
        """
        Confirma todas as alterações realizadas na transação atual.

        Returns:
            None.
        """
        self.session.commit()

    def rollback(self) -> None:
        """
        Reverte todas as alterações realizadas na transação atual.

        Returns:
            None.
        """
        self.session.rollback()