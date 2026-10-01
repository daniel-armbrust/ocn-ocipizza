#
# repositories/user_refresh_token_repository.py
#

from abc import ABC, abstractmethod
from datetime import datetime

from app.models.user_refresh_token import UserRefreshToken


class UserRefreshTokenRepository(ABC):
    """
    Define o contrato de persistência para os refresh tokens
    associados aos usuários.

    Os refresh tokens permitem renovar access tokens sem exigir
    novamente as credenciais do usuário.

    Apenas o hash do refresh token deve ser persistido. O valor
    original do token nunca deve ser armazenado no banco de dados.
    """

    @abstractmethod
    def create(self, refresh_token: UserRefreshToken) -> UserRefreshToken:
        """
        Persiste um novo refresh token.

        Args:
            refresh_token: Modelo contendo os dados do refresh token
                que será persistido.

        Returns:
            Refresh token persistido.
        """
        pass

    @abstractmethod
    def get_by_hash(self, token_hash: str) -> UserRefreshToken | None:
        """
        Retorna um refresh token a partir de seu hash.

        Args:
            token_hash: Hash do refresh token utilizado na consulta.

        Returns:
            Refresh token encontrado ou `None` caso não exista.
        """
        pass

    @abstractmethod
    def revoke(self, token_id: int, revoked_at: datetime) -> None:
        """
        Revoga um refresh token.

        A revogação mantém o registro persistido e registra o momento
        em que o token deixou de ser válido.

        Args:
            token_id: Identificador interno do refresh token.
            revoked_at: Data e hora em que o token foi revogado.

        Returns:
            None.
        """
        pass