#
# repositories/sqlalchemy/sqlalchemy_password_reset_token_repository.py
#

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.password_reset_token import PasswordResetToken

from app.repositories.orm.password_reset_token_orm import PasswordResetTokenORM
from app.repositories.password_reset_token_repository import PasswordResetTokenRepository

from app.utils.utils import bin_to_uuid, uuid_to_bin


class SqlAlchemyPasswordResetTokenRepository(PasswordResetTokenRepository):
    """
    Implementação SQLAlchemy do repositório de tokens utilizados
    no processo de redefinição de senha.

    Esta classe é responsável pelas operações de persistência e consulta
    dos tokens de redefinição de senha utilizando uma sessão SQLAlchemy.

    O token original nunca é armazenado no banco de dados. Somente seu
    hash é persistido através do modelo PasswordResetTokenORM.

    O controle de transação não pertence ao repositório. As operações
    realizadas utilizam a transação associada à sessão recebida e o
    commit ou rollback deve ser realizado através do UnitOfWork.
    """

    def __init__(self, session: Session) -> None:
        """
        Inicializa o repositório.

        Args:
            session: Sessão SQLAlchemy utilizada nas operações
                de persistência.
        """

        self.session = session

    def create(self, token: PasswordResetToken) -> PasswordResetToken:
        """
        Persiste um novo token de redefinição de senha.

        Args:
            token: Modelo contendo os dados do token que será persistido.

        Returns:
            Token de redefinição de senha persistido.

        Raises:
            SQLAlchemyError: Caso ocorra uma falha durante a persistência.
        """

        # Converte o modelo da aplicação para o modelo utilizado
        # pelo SQLAlchemy.
        orm_token = PasswordResetTokenORM(
            user_id=uuid_to_bin(token.user_id),
            token_hash=token.token_hash,
            created_at=token.created_at,
            expires_at=token.expires_at,
            used_at=token.used_at,
            revoked_at=token.revoked_at
        )

        # Adiciona o registro à sessão atual.
        self.session.add(orm_token)

        # Executa o INSERT sem finalizar a transação.
        # O commit permanece sob responsabilidade do UnitOfWork.
        self.session.flush()

        # Atualiza o objeto com valores eventualmente gerados
        # pelo banco de dados, como o identificador do registro.
        self.session.refresh(orm_token)

        return self._to_model(orm_token)

    def get_by_hash(self, token_hash: str) -> PasswordResetToken | None:
        """
        Retorna um token de redefinição de senha a partir de seu hash.

        Args:
            token_hash: Hash do token utilizado na consulta.

        Returns:
            Token encontrado ou `None` caso não exista.

        Raises:
            SQLAlchemyError: Caso ocorra uma falha durante a consulta.
        """

        orm_token = self.session.scalar(
            select(PasswordResetTokenORM).where(
                PasswordResetTokenORM.token_hash == token_hash
            )
        )

        if orm_token is None:
            return None

        return self._to_model(orm_token)

    def get_active_by_user_id(self, user_id: UUID) -> PasswordResetToken | None:
        """
        Retorna o token ativo de redefinição de senha associado
        a um usuário.

        Um token é considerado ativo quando ainda não foi utilizado,
        não foi revogado e ainda não expirou.

        Args:
            user_id: Identificador UUID do usuário.

        Returns:
            Token ativo encontrado ou `None` caso não exista.

        Raises:
            SQLAlchemyError: Caso ocorra uma falha durante a consulta.
        """

        now = datetime.now().astimezone()

        orm_token = self.session.scalar(
            select(PasswordResetTokenORM)
            .where(
                PasswordResetTokenORM.user_id == uuid_to_bin(user_id),
                PasswordResetTokenORM.used_at.is_(None),
                PasswordResetTokenORM.revoked_at.is_(None),
                PasswordResetTokenORM.expires_at > now,
            )
            .order_by(
                PasswordResetTokenORM.created_at.desc()
            )
        )

        if orm_token is None:
            return None

        return self._to_model(orm_token)

    def mark_as_used(self, token_id: int, used_at: datetime) -> None:
        """
        Marca um token de redefinição de senha como utilizado.

        Args:
            token_id: Identificador interno do token.
            used_at: Data e hora em que o token foi utilizado.

        Returns:
            None.

        Raises:
            ValueError: Caso o token informado não seja encontrado.
            SQLAlchemyError: Caso ocorra uma falha durante a persistência.
        """

        orm_token = self.session.get(PasswordResetTokenORM, token_id)

        if orm_token is None:
            raise ValueError('Password reset token not found.')

        orm_token.used_at = used_at

        # Envia a alteração para o banco mantendo a transação aberta.
        self.session.flush()

    def revoke(self, token_id: int, revoked_at: datetime) -> None:
        """
        Marca um token de redefinição de senha como revogado.

        Args:
            token_id: Identificador interno do token.
            revoked_at: Data e hora em que o token foi revogado.

        Returns:
            None.

        Raises:
            ValueError: Caso o token informado não seja encontrado.
            SQLAlchemyError: Caso ocorra uma falha durante a persistência.
        """

        orm_token = self.session.get(PasswordResetTokenORM, token_id)

        if orm_token is None:
            raise ValueError('Password reset token not found.')

        orm_token.revoked_at = revoked_at

        # Envia a alteração para o banco mantendo a transação aberta.
        self.session.flush()

    @staticmethod
    def _to_model(orm_token: PasswordResetTokenORM) -> PasswordResetToken:
        """
        Converte um modelo ORM em um modelo da aplicação.

        Args:
            orm_token: Registro SQLAlchemy que será convertido.

        Returns:
            Modelo PasswordResetToken correspondente ao registro.
        """

        return PasswordResetToken(
            id=orm_token.id,
            user_id=bin_to_uuid(orm_token.user_id),
            token_hash=orm_token.token_hash,
            created_at=orm_token.created_at,
            expires_at=orm_token.expires_at,
            used_at=orm_token.used_at,
            revoked_at=orm_token.revoked_at
        )