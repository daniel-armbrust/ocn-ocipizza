#
# repositories/sqlalchemy/sqlalchemy_user_repository.py
#

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.utils.utils import uuid_to_bin, bin_to_uuid

from app.models.user import User

from app.repositories.orm.user_orm import UserORM
from app.repositories.user_repository import UserRepository


class SqlAlchemyUserRepository(UserRepository):
    """
    Implementação do repositório de usuários utilizando SQLAlchemy.

    Responsável por persistir e consultar usuários em bancos relacionais 
    suportados pelo SQLAlchemy e converter objetos entre o modelo da
    aplicação e o modelo ORM.
    """

    def __init__(self, session: Session):
        """
        Inicializa o repositório.

        Args:
            session: Sessão SQLAlchemy utilizada nas operações de persistência.
        """
        self.session = session

    def create(self, user: User) -> User:
        """
        Persiste um novo usuário.

        Args:
            user: Usuário a ser persistido.

        Returns:
            Usuário persistido, incluindo valores gerados pelo banco.
        
        Raises:
            IntegrityError: Caso ocorra uma violação de integridade no banco
                de dados, como e-mail ou WhatsApp duplicado.

            SQLAlchemyError: Caso ocorra uma falha durante a persistência.
        """

        orm_user = UserORM(
            id=uuid_to_bin(user.id),
            full_name=user.full_name,
            email=user.email,
            whatsapp=user.whatsapp,
            password_hash=user.password_hash,
            confirmed=user.confirmed,
            is_admin=user.is_admin,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

        self.session.add(orm_user)

        # Envia as alterações pendentes ao banco sem finalizar a transação.
        # Isso permite validar a operação e sincronizar valores gerados 
        # pelo banco.
        self.session.flush()

        # Atualiza o objeto ORM com os valores efetivamente persistidos no 
        # banco.
        self.session.refresh(orm_user)

        return self._to_model(orm_user)

    def get_by_id(self, user_id: UUID) -> User | None:
        """
        Busca um usuário pelo identificador.

        Args:
            user_id: Identificador UUID do usuário.

        Returns:
            Usuário encontrado ou None caso não exista.
        
        Raises:
            SQLAlchemyError: Caso ocorra uma falha durante a consulta ao banco.
        """

        orm_user = self.session.get(UserORM, uuid_to_bin(user_id))

        if orm_user is None:
            return None

        return self._to_model(orm_user)

    def get_by_email(self, email: str) -> User | None:
        """
        Busca um usuário pelo endereço de e-mail.

        Args:
            email: Endereço de e-mail do usuário.

        Returns:
            Usuário encontrado ou None caso não exista.
        
        Raises:
            SQLAlchemyError: Caso ocorra uma falha durante a consulta ao banco.
        """

        statement = select(UserORM).where(
            UserORM.email == email
        )

        orm_user = self.session.scalar(statement)

        if orm_user is None:
            return None

        return self._to_model(orm_user)

    def get_by_whatsapp(self, whatsapp: str) -> User | None:
        """
        Busca um usuário pelo número de WhatsApp.

        Args:
            whatsapp: Número de WhatsApp do usuário.

        Returns:
            Usuário encontrado ou None caso não exista.

        Raises:
            SQLAlchemyError: Caso ocorra uma falha durante a consulta ao banco.
        """

        statement = select(UserORM).where(
            UserORM.whatsapp == whatsapp
        )

        orm_user = self.session.scalar(statement)

        if orm_user is None:
            return None

        return self._to_model(orm_user)
        
    def update(self, user: User) -> User:
        """
        Atualiza um usuário existente.

        Args:
            user: Usuário contendo os dados atualizados.

        Returns:
            Usuário atualizado.

        Raises:
            ValueError: Caso o usuário informado não seja encontrado.

            IntegrityError: Caso ocorra uma violação de integridade no banco de dados.

            SQLAlchemyError: Caso ocorra uma falha durante a atualização.
        """

        orm_user = self.session.get(
            UserORM,
            uuid_to_bin(user.id),
        )

        if orm_user is None:
            raise ValueError('User not found.')

        orm_user.full_name = user.full_name
        orm_user.email = user.email
        orm_user.whatsapp = user.whatsapp
        orm_user.password_hash = user.password_hash
        orm_user.confirmed = user.confirmed
        orm_user.is_admin = user.is_admin
        orm_user.updated_at = user.updated_at

        self.session.flush()

        return self._to_model(orm_user)

    def delete(self, user_id: UUID) -> None:
        """
        Remove um usuário.

        Args:
            user_id: Identificador UUID do usuário.

        Returns:
            None.
        
        Raises:
            ValueError: Caso o usuário informado não seja encontrado.
            
            SQLAlchemyError: Caso ocorra uma falha durante a remoção.
        """
        orm_user = self.session.get(
            UserORM,
            uuid_to_bin(user_id),
        )

        if orm_user is None:
            return

        self.session.delete(orm_user)
        self.session.flush()

    @staticmethod
    def _to_model(orm_user: UserORM) -> User:
        """
        Converte um modelo ORM em um modelo da aplicação.

        Args:
            orm_user: Usuário representado pelo modelo ORM.

        Returns:
            Usuário representado pelo modelo da aplicação.
        """

        return User(
            id=bin_to_uuid(orm_user.id),
            full_name=orm_user.full_name,
            email=orm_user.email,
            whatsapp=orm_user.whatsapp,
            password_hash=orm_user.password_hash,
            confirmed=orm_user.confirmed,
            is_admin=orm_user.is_admin,
            created_at=orm_user.created_at,
            updated_at=orm_user.updated_at
        )