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

        Raises:
            RepositoryConflictError: Caso os dados violem uma restrição de
                integridade da persistência.
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

        Raises:
            RepositoryConflictError: Caso os dados violem uma restrição de
                integridade da persistência.
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

    @abstractmethod
    def get_all(self,
                email: str | None = None,
                confirmed: bool | None = None,
                is_admin: bool | None = None,
                limit: int = 50,
                offset: int = 0) -> list[User]:
        """
        Retorna os usuários cadastrados de acordo com os filtros informados.

        Args:
            email: Parte do endereço de e-mail utilizada como filtro.
            confirmed: Filtra usuários de acordo com o estado de confirmação.
            is_admin: Filtra usuários de acordo com o privilégio administrativo.
            limit: Quantidade máxima de usuários retornados.
            offset: Quantidade de registros ignorados antes do retorno.

        Returns:
            Lista contendo os usuários encontrados.
        """
        pass

    
