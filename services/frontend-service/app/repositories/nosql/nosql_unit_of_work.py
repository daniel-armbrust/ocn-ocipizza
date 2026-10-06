#
# repositories/nosql/nosql_unit_of_work.py
#

from app.repositories.unit_of_work import UnitOfWork


class NosqlNoOpUnitOfWork(UnitOfWork):
    """
    Implementação de UnitOfWork sem controle transacional explícito.

    Utilizada por providers cujas operações são persistidas
    diretamente pelo próprio repository.
    """

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass