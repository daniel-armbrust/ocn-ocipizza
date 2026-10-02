#
# repositories/sqlalchemy/sqlalchemy_user_repository.py
#

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.utils.utils import uuid_to_bin, bin_to_uuid

from app.models.user import User

from app.exceptions.repository_exceptions import RepositoryConflictError
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
            RepositoryConflictError: Caso uma restrição de integridade seja
                violada durante a persistência.

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

        try:
            self.session.add(orm_user)

            # Envia as alterações pendentes ao banco sem finalizar a transação.
            # Isso permite validar a operação e sincronizar valores gerados
            # pelo banco.
            self.session.flush()

            # Atualiza o objeto ORM com os valores efetivamente persistidos no
            # banco.
            self.session.refresh(orm_user)
        except IntegrityError as ex:
            # Traduz a exceção do mecanismo de persistência para uma exceção
            # conhecida pela aplicação, sem interpretar mensagens ou códigos
            # específicos do banco de dados utilizado.
            raise RepositoryConflictError(
                'Unable to create user due to a data conflict.'
            ) from ex

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
            SQLAlchemyError: Caso ocorra uma falha durante a 
                consulta ao banco.
        """

        statement = select(UserORM).where(UserORM.email == email)

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
            SQLAlchemyError: Caso ocorra uma falha durante 
                a consulta ao banco.
        """

        statement = select(UserORM).where(UserORM.whatsapp == whatsapp)

        orm_user = self.session.scalar(statement)

        if orm_user is None:
            return None

        return self._to_model(orm_user)

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

        # Inicia a consulta utilizando a tabela de usuários.
        query = select(UserORM)

        # Filtro por e-mail.
        if email is not None:
            query = query.where(UserORM.email.ilike(f'%{email}%'))

        # Filtro pelo estado de confirmação.
        if confirmed is not None:
            query = query.where(UserORM.confirmed == confirmed)

        # Filtro pelo privilégio administrativo.
        if is_admin is not None:
            query = query.where(UserORM.is_admin == is_admin)

        # Ordena os usuários do mais recente para o mais antigo e aplica
        # paginação através de offset e limit.
        query = (
            query
            .order_by(UserORM.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        # Executa a consulta e retorna os registros ORM encontrados.
        orm_users = self.session.scalars(query).all()

        # Converte os registros SQLAlchemy para modelos da aplicação,
        # evitando que a camada de serviço conheça detalhes do ORM.
        return [
            self._to_model(orm_user)
            for orm_user in orm_users
        ]
        
    def update(self, user: User) -> User:
        """
        Atualiza um usuário existente.

        Args:
            user: Usuário contendo os dados atualizados.

        Returns:
            Usuário atualizado.

        Raises:
            ValueError: Caso o usuário informado não seja encontrado.

            RepositoryConflictError: Caso uma restrição de integridade seja
                violada durante a atualização.

            SQLAlchemyError: Caso ocorra uma falha durante a atualização.
        """

        orm_user = self.session.get(
            UserORM,
            uuid_to_bin(user.id)
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

        try:
            self.session.flush()
        except IntegrityError as ex:
            raise RepositoryConflictError(
                'Unable to update user due to a data conflict.'
            ) from ex

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
            uuid_to_bin(user_id)
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
