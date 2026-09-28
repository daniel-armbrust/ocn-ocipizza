#
# repositories/unit_of_work.py
#

from abc import ABC, abstractmethod


class UnitOfWork(ABC):
    """
    Define o contrato para controle de transações da camada de persistência.
    """

    @abstractmethod
    def commit(self) -> None:
        """
        Confirma as operações realizadas na transação atual.

        Returns:
            None.
        """
        pass

    @abstractmethod
    def rollback(self) -> None:
        """
        Reverte as operações realizadas na transação atual.

        Returns:
            None.
        """
        pass