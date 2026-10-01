#
# repositories/password_reset_token_repository.py
#

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.models.password_reset_token import PasswordResetToken


class PasswordResetTokenRepository(ABC):
    """
    Define o contrato de persistência para os tokens utilizados no processo de redefinição de senha.

    O repositório trabalha somente com o hash do token. O token original nunca deve ser armazenado no banco de dados.
    """

    @abstractmethod
    def create(self, token: PasswordResetToken) -> PasswordResetToken:
        """
        Persiste um novo token de redefinição de senha.

        Args:
            token: Modelo contendo os dados do token que será persistido.

        Returns:
            Token de redefinição de senha persistido.
        """
        pass

    @abstractmethod
    def get_by_hash(self, token_hash: str) -> PasswordResetToken | None:
        """
        Retorna um token de redefinição de senha a partir de seu hash.

        Args:
            token_hash: Hash do token utilizado na consulta.

        Returns:
            Token encontrado ou `None` caso não exista.
        """
        pass

    @abstractmethod
    def get_active_by_user_id(self, user_id: UUID) -> PasswordResetToken | None:
        """
        Retorna o token ativo de redefinição de senha associado a um usuário.

        Um token ativo é aquele que ainda não foi utilizado,
        revogado ou expirado.

        Args:
            user_id: Identificador UUID do usuário.

        Returns:
            Token ativo encontrado ou `None` caso não exista.
        """
        pass

    @abstractmethod
    def mark_as_used(self, token_id: int, used_at: datetime) -> None:
        """
        Marca um token de redefinição de senha como utilizado.

        Args:
            token_id: Identificador interno do token.
            used_at: Data e hora em que o token foi utilizado.

        Returns:
            None.
        """
        pass

    @abstractmethod
    def revoke(self, token_id: int, revoked_at: datetime) -> None:
        """
        Marca um token de redefinição de senha como revogado.

        Args:
            token_id: Identificador interno do token.
            revoked_at: Data e hora em que o token foi revogado.

        Returns:
            None.
        """
        pass