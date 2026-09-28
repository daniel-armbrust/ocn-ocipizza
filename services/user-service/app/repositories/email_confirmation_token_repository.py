#
# repositories/email_confirmation_token_repository.py
#

from abc import ABC, abstractmethod
from uuid import UUID

from app.models.email_confirmation_token import EmailConfirmationToken


class EmailConfirmationTokenRepository(ABC):
    """
    Define o contrato de persistência dos tokens de confirmação de e-mail.
    """

    @abstractmethod
    def create(self, token: EmailConfirmationToken) -> EmailConfirmationToken:
        """
        Persiste um novo token de confirmação de e-mail.

        Args:
            token: Token de confirmação a ser persistido.

        Returns:
            Token de confirmação persistido.
        """
        pass

    @abstractmethod
    def get_by_token_hash(self, token_hash: str) -> EmailConfirmationToken | None:
        """
        Busca um token de confirmação pelo seu hash.

        Args:
            token_hash: Hash do token de confirmação.

        Returns:
            Token encontrado ou None caso não exista.
        """
        pass

    @abstractmethod
    def get_active_by_user_id(self, user_id: UUID) -> EmailConfirmationToken | None:
        """
        Busca o token de confirmação ativo de um usuário.

        Args:
            user_id: Identificador UUID do usuário.

        Returns:
            Token ativo encontrado ou None caso não exista.
        """
        pass

    @abstractmethod
    def update(self, token: EmailConfirmationToken) -> EmailConfirmationToken:
        """
        Atualiza um token de confirmação de e-mail.

        Args:
            token: Token contendo os dados atualizados.

        Returns:
            Token de confirmação atualizado.
        """
        pass