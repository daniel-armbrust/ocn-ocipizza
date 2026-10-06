#
# repositories/session_repository.py
#

from abc import ABC, abstractmethod
from typing import Any


class SessionRepository(ABC):
    """
    Define o contrato utilizado para persistência das sessões
    mantidas pelo frontend-service.

    A implementação concreta pode utilizar Redis, Oracle NoSQL,
    SQLAlchemy ou outro mecanismo de persistência.
    """

    @abstractmethod
    async def create(self,
                     session_id: str,
                     data: dict[str, Any],
                     ttl: int) -> None:
        """
        Cria uma nova sessão.

        Args:
            session_id: Identificador único da sessão.
            data: Dados associados à sessão.
            ttl: Tempo de validade da sessão, em segundos.
        """
        pass

    @abstractmethod
    async def get(self, session_id: str) -> dict[str, Any] | None:
        """
        Retorna os dados associados a uma sessão.

        Args:
            session_id: Identificador único da sessão.

        Returns:
            Dados da sessão ou `None` caso ela não exista
            ou tenha expirado.
        """
        pass

    @abstractmethod
    async def update(self,
                     session_id: str,
                     data: dict[str, Any],
                     ttl: int | None = None) -> None:
        """
        Atualiza os dados associados a uma sessão.

        Args:
            session_id: Identificador único da sessão.
            data: Novos dados associados à sessão.
            ttl: Novo tempo de validade da sessão, em segundos.
                Quando não informado, mantém a expiração atual.
        """
        pass

    @abstractmethod
    async def delete(self, session_id: str) -> None:
        """
        Remove uma sessão.

        Args:
            session_id: Identificador único da sessão.
        """
        pass

    @abstractmethod
    async def exists(self, session_id: str) -> bool:
        """
        Verifica se uma sessão existe.

        Args:
            session_id: Identificador único da sessão.

        Returns:
            `True` quando a sessão existir e estiver válida;
            caso contrário, `False`.
        """
        pass