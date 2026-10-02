#
# services/user_service_admin.py
#

from uuid import UUID, uuid4

from fastapi import Depends

from app.dependencies.database import get_unit_of_work, get_user_repository

from app.exceptions.user_exceptions import (
    UserAlreadyExistsError,
    UserCreationError,
    UserDeletionError,
    UserNotFoundError,
    UserQueryError,
    UserUpdateError
)

from app.models.user import User
from app.repositories.unit_of_work import UnitOfWork
from app.exceptions.repository_exceptions import RepositoryConflictError
from app.repositories.user_repository import UserRepository

from app.schemas.user_admin_schema import (
    UserAdminCreateRequest,
    UserAdminUpdateRequest
)

from app.services.user_email_service import (
    UserEmailService,
    get_user_email_service
)

from app.services.user_password_service import (
    UserPasswordService,
    get_user_password_service
)

from app.utils.utils import normalize_email, now_utc


class UserServiceAdmin:
    """Serviço responsável pelos casos de uso administrativos de usuários."""

    def __init__(
        self,
        unit_of_work: UnitOfWork,
        user_password_service: UserPasswordService,
        user_email_service: UserEmailService,
        user_repository: UserRepository) -> None:
        """
        Inicializa o serviço administrativo de usuários.

        Args:
            unit_of_work: Unidade de trabalho responsável pelas transações.
            user_password_service: Serviço responsável pelas senhas.
            user_email_service: Serviço responsável pelos e-mails.
            user_repository: Repositório utilizado para persistência.
        """

        self.unit_of_work = unit_of_work
        self.user_password_service = user_password_service
        self.user_email_service = user_email_service
        self.user_repository = user_repository

    def create(self, payload: UserAdminCreateRequest) -> User:
        """
        Cria um usuário por meio de uma operação administrativa.

        Args:
            payload: Dados necessários para criação do usuário.

        Returns:
            Usuário criado.

        Raises:
            UserAlreadyExistsError: Caso e-mail ou WhatsApp já esteja cadastrado.
            UserCreationError: Caso não seja possível criar o usuário.
        """

        email = normalize_email(payload.email)

        try:
            if self.user_repository.get_by_email(email) is not None:
                raise UserAlreadyExistsError('User email already registered.')

            if self.user_repository.get_by_whatsapp(payload.whatsapp) is not None:
                raise UserAlreadyExistsError(
                    'User WhatsApp already registered.'
                )

            now = now_utc()

            user = User(
                id=uuid4(),
                full_name=payload.full_name,
                email=email,
                whatsapp=payload.whatsapp,
                password_hash=self.user_password_service.hash_password(
                    payload.password
                ),
                confirmed=payload.confirmed,
                is_admin=payload.is_admin,
                created_at=now,
                updated_at=now
            )

            user = self.user_repository.create(user)

            if not user.confirmed:
                self.user_email_service.publish_confirmation_email(user)

            self.unit_of_work.commit()
        except UserAlreadyExistsError:
            self.unit_of_work.rollback()
            raise
        except RepositoryConflictError as ex:
            self.unit_of_work.rollback()
            raise UserAlreadyExistsError(
                'User email or WhatsApp already registered.'
            ) from ex
        except Exception as ex:
            self.unit_of_work.rollback()
            raise UserCreationError('Error creating user.') from ex

        return user

    def update(self, user_id: UUID, payload: UserAdminUpdateRequest) -> User:
        """
        Atualiza um usuário por meio de uma operação administrativa.

        Args:
            user_id: Identificador UUID do usuário.
            payload: Dados utilizados na atualização.

        Returns:
            Usuário atualizado.

        Raises:
            UserNotFoundError: Caso o usuário não seja encontrado.
            UserAlreadyExistsError: Caso e-mail ou WhatsApp já esteja cadastrado.
            UserUpdateError: Caso não seja possível atualizar o usuário.
        """

        user = self.user_repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError('User not found.')

        email = normalize_email(payload.email)

        if email != user.email:
            existing_user = self.user_repository.get_by_email(email)

            if existing_user is not None and existing_user.id != user.id:
                raise UserAlreadyExistsError('User email already registered.')

        if payload.whatsapp != user.whatsapp:
            existing_user = self.user_repository.get_by_whatsapp(payload.whatsapp)

            if existing_user is not None and existing_user.id != user.id:
                raise UserAlreadyExistsError('User WhatsApp already registered.')

        user.full_name = payload.full_name
        user.email = email
        user.whatsapp = payload.whatsapp
        user.confirmed = payload.confirmed
        user.is_admin = payload.is_admin
        user.updated_at = now_utc()

        try:
            user = self.user_repository.update(user)
            self.unit_of_work.commit()
        except RepositoryConflictError as ex:
            self.unit_of_work.rollback()
            raise UserAlreadyExistsError(
                'User email or WhatsApp already registered.'
            ) from ex
        except Exception as ex:
            self.unit_of_work.rollback()
            raise UserUpdateError('Error updating user.') from ex

        return user

    def confirm(self, user_id: UUID) -> User:
        """
        Confirma administrativamente o cadastro de um usuário.

        Args:
            user_id: Identificador UUID do usuário.

        Returns:
            Usuário confirmado.

        Raises:
            UserNotFoundError: Caso o usuário não seja encontrado.
            UserUpdateError: Caso não seja possível confirmar o usuário.
        """

        user = self.user_repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError('User not found.')

        if user.confirmed:
            return user

        user.confirmed = True
        user.updated_at = now_utc()

        try:
            user = self.user_repository.update(user)
            self.unit_of_work.commit()
        except Exception as ex:
            self.unit_of_work.rollback()
            raise UserUpdateError('Error confirming user.') from ex

        return user

    def delete(self, user_id: UUID) -> None:
        """
        Remove um usuário por meio de uma operação administrativa.

        Args:
            user_id: Identificador UUID do usuário.

        Returns:
            None.

        Raises:
            UserNotFoundError: Caso o usuário não seja encontrado.
            UserDeletionError: Caso não seja possível remover o usuário.
        """

        if self.user_repository.get_by_id(user_id) is None:
            raise UserNotFoundError('User not found.')

        try:
            self.user_repository.delete(user_id)
            self.unit_of_work.commit()
        except Exception as ex:
            self.unit_of_work.rollback()
            raise UserDeletionError('Error deleting user.') from ex

    def get_by_id(self, user_id: UUID) -> User:
        """
        Retorna um usuário pelo identificador.

        Args:
            user_id: Identificador UUID do usuário.

        Returns:
            Usuário encontrado.

        Raises:
            UserNotFoundError: Caso o usuário não seja encontrado.
        """

        user = self.user_repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError('User not found.')

        return user

    def get_all(self,
                email: str | None = None,
                confirmed: bool | None = None,
                is_admin: bool | None = None,
                limit: int = 50,
                offset: int = 0) -> list[User]:
        """
        Retorna os usuários de acordo com os filtros administrativos.

        Args:
            email: Parte do endereço de e-mail utilizada como filtro.
            confirmed: Filtra pelo estado de confirmação.
            is_admin: Filtra pelo privilégio administrativo.
            limit: Quantidade máxima de usuários retornados.
            offset: Quantidade de registros ignorados.

        Returns:
            Lista de usuários encontrados.

        Raises:
            UserQueryError: Caso ocorra uma falha durante a consulta.
        """

        try:
            return self.user_repository.get_all(
                email=email,
                confirmed=confirmed,
                is_admin=is_admin,
                limit=limit,
                offset=offset
            )
        except Exception as ex:
            raise UserQueryError('Error retrieving users.') from ex


def get_user_service_admin(
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
    user_password_service: UserPasswordService = Depends(
        get_user_password_service
    ),
    user_email_service: UserEmailService = Depends(get_user_email_service),
    user_repository: UserRepository = Depends(get_user_repository)
) -> UserServiceAdmin:
    """
    Monta o serviço administrativo de usuários.

    Args:
        unit_of_work: Unidade de trabalho responsável pelas transações.
        user_password_service: Serviço responsável pelas senhas.
        user_email_service: Serviço responsável pelos e-mails.
        user_repository: Repositório utilizado para persistência.

    Returns:
        Instância de `UserServiceAdmin`.
    """

    return UserServiceAdmin(
        unit_of_work=unit_of_work,
        user_password_service=user_password_service,
        user_email_service=user_email_service,
        user_repository=user_repository
    )
