#
# repositories/user_address_repository.py
#

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.models.user_address import UserAddress


class UserAddressRepository(ABC):
    """
    Define o contrato para persistência de endereços de usuário.
    """

    @abstractmethod
    def create(self, address: UserAddress) -> UserAddress:
        """
        Cria um novo endereço para o usuário.

        Args:
            address: Endereço que será persistido.

        Returns:
            O endereço persistido.
        """
        pass

    @abstractmethod
    def get_by_id(self, address_id: UUID) -> UserAddress | None:
        """
        Busca um endereço pelo identificador.

        Args:
            address_id: Identificador único do endereço.

        Returns:
            O endereço encontrado ou None caso não exista.
        """
        pass

    @abstractmethod
    def get_by_id_and_user_id(self,
                              address_id: UUID,
                              user_id: UUID) -> UserAddress | None:
        """
        Busca um endereço pelo identificador e pelo usuário proprietário.

        Args:
            address_id: Identificador único do endereço.
            user_id: Identificador único do usuário proprietário do endereço.

        Returns:
            O endereço encontrado ou None caso não exista ou não pertença
            ao usuário informado.
        """
        pass

    @abstractmethod
    def get_by_user_id(self,
                       user_id: UUID) -> list[UserAddress]:
        """
        Retorna todos os endereços pertencentes ao usuário.

        Args:
            user_id: Identificador único do usuário.

        Returns:
            Lista de endereços pertencentes ao usuário.
        """
        pass

    @abstractmethod
    def get_default_by_user_id(self,
                               user_id: UUID) -> UserAddress | None:
        """
        Retorna o endereço padrão do usuário.

        Args:
            user_id: Identificador único do usuário.

        Returns:
            O endereço padrão do usuário ou None caso não exista.
        """
        pass

    @abstractmethod
    def update(self,
               address_id: UUID,
               address: UserAddress) -> UserAddress:
        """
        Atualiza os dados de um endereço.

        Args:
            address_id: Identificador único do endereço.
            address: Dados atualizados do endereço.

        Returns:
            O endereço atualizado.
        """
        pass

    @abstractmethod
    def unset_default_by_user_id(self,
                                 user_id: UUID,
                                 updated_at: datetime) -> None:
        """
        Remove a marcação de endereço padrão dos endereços do usuário.

        Args:
            user_id: Identificador único do usuário.
            updated_at: Data e hora da atualização em UTC.

        Returns:
            None.
        """
        pass

    @abstractmethod
    def delete(self,
               address_id: UUID,
               user_id: UUID) -> bool:
        """
        Remove um endereço pertencente ao usuário.

        Args:
            address_id: Identificador único do endereço.
            user_id: Identificador único do usuário proprietário do endereço.

        Returns:
            True caso o endereço tenha sido removido ou False caso nenhum
            endereço correspondente tenha sido encontrado.
        """
        pass