#
# repositories/sqlalchemy/sqlalchemy_user_email_confirmation_token_repository.py
#

from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.user_email_confirmation_token import UserEmailConfirmationToken
from app.repositories.user_email_confirmation_token_repository import UserEmailConfirmationTokenRepository
from app.repositories.orm.user_email_confirmation_token_orm import UserEmailConfirmationTokenORM

from app.utils.utils import bin_to_uuid, uuid_to_bin


class SqlAlchemyUserEmailConfirmationTokenRepository(
    UserEmailConfirmationTokenRepository
):
    """
    Implementação do repositório de tokens de confirmação de e-mail
    utilizando SQLAlchemy.
    """

    def __init__(self, session: Session) -> None:
        """
        Inicializa o repositório.

        Args:
            session: Sessão SQLAlchemy utilizada para persistência.
        """

        self.session = session

    def create(self, token: UserEmailConfirmationToken) -> UserEmailConfirmationToken:
        """
        Persiste um novo token de confirmação de e-mail.

        Args:
            token: Token de confirmação a ser persistido.

        Returns:
            Token de confirmação persistido.

        Raises:
            IntegrityError: Caso ocorra uma violação de integridade no banco
                de dados, como token duplicado.

            SQLAlchemyError: Caso ocorra uma falha durante a persistência.
        """

        orm_token = UserEmailConfirmationTokenORM(
            user_id=uuid_to_bin(token.user_id),
            token_hash=token.token_hash,
            created_at=token.created_at,
            expires_at=token.expires_at,
            used_at=token.used_at,
            revoked_at=token.revoked_at,
        )

        self.session.add(orm_token)

        # Envia as alterações pendentes ao banco sem finalizar a transação.
        # Isso permite validar a operação e sincronizar valores gerados 
        # pelo banco.
        self.session.flush()

        # Atualiza o objeto ORM com valores gerados pelo banco,
        # como o ID auto incremental.
        self.session.refresh(orm_token)

        return self._to_model(orm_token)

    def get_by_token_hash(self, token_hash: str) -> UserEmailConfirmationToken | None:
        """
        Busca um token de confirmação pelo seu hash.

        Args:
            token_hash: Hash do token de confirmação.

        Returns:
            Token encontrado ou None caso não exista.

        Raises:
            SQLAlchemyError: Caso ocorra uma falha durante a consulta ao banco.
        """
        
        statement = select(
            UserEmailConfirmationTokenORM
        ).where(
            UserEmailConfirmationTokenORM.token_hash == token_hash
        )

        orm_token = self.session.scalar(statement)

        if orm_token is None:
            return None

        return self._to_model(orm_token)

    def get_active_by_user_id(self, user_id: UUID) -> UserEmailConfirmationToken | None:
        """
        Busca o token ativo de confirmação de um usuário.

        Um token ativo é aquele que não foi utilizado,
        não foi revogado e ainda não expirou.

        Args:
            user_id: Identificador UUID do usuário.

        Returns:
            Token ativo encontrado ou None caso não exista.

        Raises:
            SQLAlchemyError: Caso ocorra uma falha durante a consulta ao banco.
        """

        statement = (
            select(UserEmailConfirmationTokenORM)
            .where(
                UserEmailConfirmationTokenORM.user_id == uuid_to_bin(user_id)
            )
            .where(
                UserEmailConfirmationTokenORM.used_at.is_(None)
            )
            .where(
                UserEmailConfirmationTokenORM.revoked_at.is_(None)
            )
        )

        orm_token = self.session.scalar(statement)

        if orm_token is None:
            return None

        return self._to_model(orm_token)

    def mark_as_used(self, token_id: int, used_at: datetime) -> bool:
        """
        Marca atomicamente um token de confirmação como utilizado.

        Args:
            token_id: Identificador interno do token.
            used_at: Data e hora em que o token foi utilizado.

        Returns:
            True quando o token foi consumido ou False quando ele já foi
            utilizado, revogado, expirou ou não existe.
        """

        statement = (
            update(UserEmailConfirmationTokenORM)
                .where(UserEmailConfirmationTokenORM.id == token_id)
                .where(UserEmailConfirmationTokenORM.used_at.is_(None))
                .where(UserEmailConfirmationTokenORM.revoked_at.is_(None))
                .where(UserEmailConfirmationTokenORM.expires_at > used_at)
                .values(used_at=used_at)
        )

        result = self.session.execute(statement)
        self.session.flush()

        return result.rowcount == 1

    @staticmethod
    def _to_model(orm_token: UserEmailConfirmationTokenORM) -> UserEmailConfirmationToken:
        """
        Converte um modelo ORM em um modelo da aplicação.

        Args:
            orm_token: Modelo ORM do token.

        Returns:
            Modelo de domínio do token.
        """

        return UserEmailConfirmationToken(
            id=orm_token.id,
            user_id=bin_to_uuid(orm_token.user_id),
            token_hash=orm_token.token_hash,
            created_at=orm_token.created_at,
            expires_at=orm_token.expires_at,
            used_at=orm_token.used_at,
            revoked_at=orm_token.revoked_at,
        )
