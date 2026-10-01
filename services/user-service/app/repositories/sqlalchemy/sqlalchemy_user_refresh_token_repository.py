#
# repositories/sqlalchemy/sqlalchemy_user_refresh_token_repository.py
#

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_refresh_token import UserRefreshToken
from app.repositories.orm.user_refresh_token_orm import UserRefreshTokenORM

from app.repositories.user_refresh_token_repository import UserRefreshTokenRepository

from app.utils.utils import bin_to_uuid, uuid_to_bin


class SqlAlchemyUserRefreshTokenRepository(UserRefreshTokenRepository):
    """
    Implementação SQLAlchemy do repositório de refresh tokens
    associados aos usuários.

    Esta classe é responsável pelas operações de persistência,
    consulta e revogação dos refresh tokens utilizando uma sessão
    SQLAlchemy.

    Apenas o hash do refresh token é persistido no banco de dados.
    O token original nunca deve ser armazenado.

    O controle da transação não pertence ao repositório. O commit
    ou rollback deve ser realizado pelo UnitOfWork responsável pelo
    caso de uso.
    """

    def __init__(self, session: Session) -> None:
        """
        Inicializa o repositório.

        Args:
            session: Sessão SQLAlchemy utilizada nas operações
                de persistência.

        Returns:
            None.
        """

        self.session = session

    def create(self, refresh_token: UserRefreshToken) -> UserRefreshToken:
        """
        Persiste um novo refresh token associado a um usuário.

        Args:
            refresh_token: Modelo contendo os dados do refresh token
                que será persistido.

        Returns:
            Refresh token persistido.

        Raises:
            SQLAlchemyError: Caso ocorra uma falha durante
                a persistência.
        """

        # Converte o modelo da aplicação para o modelo utilizado
        # pelo SQLAlchemy.
        orm_refresh_token = UserRefreshTokenORM(
            user_id=uuid_to_bin(refresh_token.user_id),
            token_hash=refresh_token.token_hash,
            created_at=refresh_token.created_at,
            expires_at=refresh_token.expires_at,
            revoked_at=refresh_token.revoked_at
        )

        # Adiciona o refresh token à sessão atual.
        self.session.add(orm_refresh_token)

        # Executa o INSERT sem finalizar a transação.
        # O commit permanece sob responsabilidade do UnitOfWork.
        self.session.flush()

        # Atualiza o objeto ORM com valores gerados pelo banco,
        # como o identificador do registro.
        self.session.refresh(orm_refresh_token)

        return self._to_model(orm_refresh_token)

    def get_by_hash(self, token_hash: str) -> UserRefreshToken | None:
        """
        Retorna um refresh token a partir de seu hash.

        Args:
            token_hash: Hash do refresh token utilizado na consulta.

        Returns:
            Refresh token encontrado ou `None` caso não exista.

        Raises:
            SQLAlchemyError: Caso ocorra uma falha durante
                a consulta.
        """

        # Consulta o refresh token utilizando seu hash, que é único
        # na tabela.
        orm_refresh_token = self.session.scalar(
            select(UserRefreshTokenORM).where(
                UserRefreshTokenORM.token_hash == token_hash
            )
        )

        if orm_refresh_token is None:
            return None

        return self._to_model(orm_refresh_token)

    def revoke(self, token_id: int, revoked_at: datetime) -> None:
        """
        Revoga um refresh token.

        A revogação mantém o registro no banco de dados e apenas
        registra o momento em que o token deixou de ser válido.

        Args:
            token_id: Identificador interno do refresh token.
            revoked_at: Data e hora em que o token foi revogado.

        Returns:
            None.

        Raises:
            ValueError: Caso o refresh token não seja encontrado.
            SQLAlchemyError: Caso ocorra uma falha durante
                a persistência.
        """

        # Localiza o refresh token através de sua chave primária.
        orm_refresh_token = self.session.get(UserRefreshTokenORM, token_id)

        if orm_refresh_token is None:
            raise ValueError('Refresh token not found.')

        # Registra o momento da revogação.
        # O token permanece armazenado para permitir rastreabilidade
        # e impedir sua reutilização.
        orm_refresh_token.revoked_at = revoked_at

        # Envia a alteração para o banco mantendo a transação aberta.
        # O commit será realizado pelo UnitOfWork.
        self.session.flush()

    @staticmethod
    def _to_model(orm_refresh_token: UserRefreshTokenORM) -> UserRefreshToken:
        """
        Converte um modelo ORM em um modelo da aplicação.

        Args:
            orm_refresh_token: Registro SQLAlchemy que será convertido.

        Returns:
            Modelo `UserRefreshToken` correspondente ao registro.
        """

        return UserRefreshToken(
            id=orm_refresh_token.id,
            user_id=bin_to_uuid(orm_refresh_token.user_id),
            token_hash=orm_refresh_token.token_hash,
            created_at=orm_refresh_token.created_at,
            expires_at=orm_refresh_token.expires_at,
            revoked_at=orm_refresh_token.revoked_at
        )