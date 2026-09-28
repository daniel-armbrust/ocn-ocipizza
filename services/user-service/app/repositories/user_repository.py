#
# repositories/user_repository.py
#

from abc import ABC, abstractmethod
from uuid import UUID

from app.models.user import User


class UserRepository(ABC):
    """
    Contrato de persistência para usuários.

    Define as operações que qualquer implementação de repositório
    de usuários deve fornecer, independentemente da tecnologia
    de persistência utilizada.
    """

    @abstractmethod
    def create(self, user: User) -> User:
        """
        Persiste um novo usuário.

        Args:
            user: Usuário a ser persistido.

        Returns:
            Usuário persistido.
        """
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        """
        Atualiza os dados de um usuário.

        Args:
            user: Usuário contendo os dados atualizados.

        Returns:
            Usuário atualizado.
        """
        pass

    @abstractmethod
    def delete(self, user_id: UUID) -> None:
        """
        Remove um usuário.

        Args:
            user_id: Identificador do usuário.
        """
        pass

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None:
        """
        Busca um usuário pelo identificador.

        Args:
            user_id: Identificador do usuário.

        Returns:
            Usuário encontrado ou None caso não exista.
        """
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        """
        Busca um usuário pelo endereço de e-mail.

        Args:
            email: Endereço de e-mail do usuário.

        Returns:
            Usuário encontrado ou None caso não exista.
        """
        pass

    @abstractmethod
    def get_by_whatsapp(self, whatsapp: str) -> User | None:
        """
        Busca um usuário pelo número de WhatsApp. 
        
        Args: 
            whatsapp: Número de WhatsApp do usuário. 
        
        Returns: 
            Usuário encontrado ou None caso não exista.
        """
        pass

    