#
# services/user_service.py
# 

from uuid import uuid4, UUID
from datetime import datetime

from fastapi import Depends

from app.utils.utils import normalize_email, now_utc

from app.models.user import User
from app.models.user_email_confirmation_token import UserEmailConfirmationToken

from app.schemas.user_schema import (
    UserCreateRequest, 
    UserUpdateRequest
)

from app.exceptions.user_exceptions import (
    UserAlreadyExistsError, 
    UserCreationError, 
    UserNotFoundError, 
    UserUpdateError,
    UserDeletionError,
    UserEmailConfirmationError,
    UserInvalidEmailConfirmationTokenError
) 

from app.repositories.unit_of_work import UnitOfWork
from app.dependencies.database import get_unit_of_work

from app.repositories.user_repository import UserRepository
from app.dependencies.database import get_user_repository

from app.services.user_password_service import (
    UserPasswordService, 
    get_user_password_service
)

from app.services.user_email_service import (
    UserEmailService,
    get_user_email_service
)


class UserService:
    """
    Serviço responsável pelos casos de uso relacionados aos usuários.

    Esta camada concentra as regras de negócio do domínio de usuários,
    coordenando operações como criação, atualização, consulta e remoção
    de usuários.

    O serviço não possui conhecimento sobre detalhes de infraestrutura,
    como banco de dados, ORM ou mecanismo de mensageria. Essas dependências
    são fornecidas através de abstrações como repositories, UnitOfWork e
    serviços especializados.

    A responsabilidade transacional permanece no caso de uso através do
    UnitOfWork, garantindo que operações relacionadas sejam confirmadas ou
    revertidas como uma única unidade de trabalho.
    """

    def __init__(self,
                 unit_of_work: UnitOfWork,
                 user_password_service: UserPasswordService,
                 user_email_service: UserEmailService,
                 user_repository: UserRepository                 
                 ) -> None:
        """
        Inicializa o serviço de usuários.

        Args:
            unit_of_work: Unidade de trabalho responsável pelo controle da transação. 
            user_password_service: Serviço responsável pelas operações relacionadas 
                à senha do usuário. 
            user_email_service: Serviço responsável pela publicação das solicitações 
                de envio de e-mail relacionadas ao usuário. 
            user_repository: Repositório utilizado para persistência de usuários.
        """

        self.unit_of_work = unit_of_work
        self.user_repository = user_repository
        self.user_password_service = user_password_service
        self.user_email_service = user_email_service

    def create(self, payload: UserCreateRequest) -> User:
        """
        Valida a unicidade dos dados, gera o hash da senha, persiste o usuário
        e solicita o envio do e-mail de confirmação.

        Args:
            payload: Dados necessários para criação do usuário.

        Returns:
            Usuário criado.

        Raises:
            UserAlreadyExistsError: Se o e-mail ou WhatsApp já estiver cadastrado.
            UserCreationError: Se não for possível concluir a criação do usuário.
        """

        normalized_email = normalize_email(payload.email)

        if self.user_repository.get_by_email(normalized_email):
            raise UserAlreadyExistsError('Email is already registered.')

        if self.user_repository.get_by_whatsapp(payload.whatsapp):
            raise UserAlreadyExistsError('WhatsApp number is already registered.')

        now = now_utc()

        user = User(
            id=uuid4(),
            full_name=payload.full_name,
            email=email,
            whatsapp=payload.whatsapp,
            password_hash=self.user_password_service.hash_password(
                payload.password
            ),
            confirmed=False,
            is_admin=False,
            created_at=now,
            updated_at=now
        )

        try:
            # Cria o usuário.
            user = self.user_repository.create(user)

            # Publica o e-mail de confirmação que será enviado ao usuário 
            # para que ele possa confirmar o seu cadastro.
            self.user_email_service.publish_confirmation_email(user)

            self.unit_of_work.commit()

            return user            
        except Exception as ex:
            self.unit_of_work.rollback()
            raise UserCreationError('Error creating user.') from ex

    def update(self, user_id: UUID, payload: UserUpdateRequest) -> User:
        """
        Atualiza os dados de um usuário existente. 
        
        Args: 
            user_id: Identificador UUID do usuário. 
            payload: Dados que serão atualizados. 
            
        Returns: 
            Usuário atualizado. 
        
        Raises:
            UserNotFoundError: Caso o usuário não seja encontrado.
            UserUpdateError: Caso ocorra falha durante a atualização. 
        """

        try:
            user = self.user_repository.get_by_id(user_id)

            if user is None:
                raise UserNotFoundError('User not found.')

            user.whatsapp = payload.whatsapp
            user.updated_at = now_utc()

            user = self.user_repository.update(user)

            self.unit_of_work.commit()
            
            return user
        except UserNotFoundError:
            raise
        except Exception as ex:
            self.unit_of_work.rollback()
            raise UserUpdateError('Error updating the user.') from ex

    def delete(self, user_id: UUID) -> None:
        """
        Remove um usuário existente. 
        
        Args: 
            user_id: Identificador UUID do usuário. 
        
        Returns: 
            None. 
        
        Raises: 
            UserNotFoundError: Se o usuário não for encontrado. 
        """

        user = self.user_repository.get_by_id(user_id) 
        
        if user is None: 
            raise UserNotFoundError('User not found.')
        
        try: 
            self.user_repository.delete(user_id) 
            
            self.unit_of_work.commit() 
        except Exception: 
            self.unit_of_work.rollback() 
            raise UserDeletionError('Error deleting the user.')

    def confirm_email(self, email: str, token: str) -> None:
        """
        Confirma o endereço de e-mail associado ao cadastro de um usuário.

        O usuário é localizado através do endereço de e-mail informado e o
        token recebido é validado antes da confirmação do cadastro.

        Args:
            email: Endereço de e-mail associado ao usuário.
            token: Token de confirmação recebido pelo usuário.

        Returns:
            None.

        Raises:
            UserNotFoundError: Caso o usuário associado ao endereço de e-mail
                não seja encontrado.
            UserInvalidEmailConfirmationTokenError: Caso o token seja inválido,
                expirado, já utilizado, revogado ou não pertença ao usuário.
            UserEmailConfirmationError: Caso ocorra uma falha durante a consulta
                ou persistência dos dados necessários à confirmação do usuário.
        """

        normalized_email = normalize_email(email)

        try:
            # Localiza o usuário associado ao endereço de e-mail informado.
            user = self.user_repository.get_by_email(normalized_email)
        except Exception as ex:
            raise UserEmailConfirmationError(
                'Error retrieving user for email confirmation.'
            ) from ex

        if user is None:
            raise UserNotFoundError('User not found.')

        # Gera o hash do token recebido, pois somente o hash
        # do token é armazenado no banco de dados.
        token_hash = self.token_service.hash_token(token)

        try:
            # Localiza o token de confirmação através de seu hash.
            email_confirmation_token = (
                self.email_confirmation_token_repository.get_by_hash(token_hash)
            )
        except Exception as ex:
            raise UserEmailConfirmationError(
                'Error retrieving email confirmation token.'
            ) from ex

        now = now_utc()

        # Valida se o token existe e ainda pode ser utilizado.
        email_confirmation_token = (
            self._validate_email_confirmation_token(email_confirmation_token, now)
        )

        # Garante que o token realmente pertence ao usuário
        # correspondente ao endereço de e-mail informado.
        if email_confirmation_token.user_id != user.id:
            raise UserInvalidEmailConfirmationTokenError(
                'Email confirmation token does not belong to the user.'
            )

        # Caso o usuário já esteja confirmado, não é necessário
        # realizar nenhuma nova alteração.
        if user.confirmed:
            return

        user.confirmed = True
        user.updated_at = now

        try:
            # Persiste a alteração do usuário.
            self.user_repository.update(user)

            # Marca o token como utilizado para impedir sua reutilização.
            self.email_confirmation_token_repository.mark_as_used(
                email_confirmation_token.id,
                now
            )

            self.unit_of_work.commit()
        except Exception as ex:
            self.unit_of_work.rollback()
            raise UserEmailConfirmationError('Error confirming user email.') from ex        

    def get_by_id(self, user_id: UUID) -> User:
        """
        Retorna um usuário a partir de seu identificador.

        Args:
            user_id: Identificador UUID do usuário.

        Returns:
            Usuário correspondente ao identificador informado.

        Raises:
            UserNotFoundError: Caso o usuário não seja encontrado.
        """
        
        user = self.user_repository.get_by_id(user_id) 
        
        if user is None: 
            raise UserNotFoundError('User not found.') 
        
        return user

    def get_by_email(self, email: str) -> User:
        """
        Busca um usuário pelo endereço de e-mail. 
        
        Args: 
            email: Endereço de e-mail do usuário. 
        
        Returns: 
            Usuário encontrado. 
        
        Raises: 
            UserNotFoundError: Se o usuário não for encontrado. 
        """
        
        normalized_email = normalize_email(email) 
        
        user = self.user_repository.get_by_email(normalized_email) 
        
        if user is None: 
            raise UserNotFoundError('User not found.') 
        
        return user

    def _validate_email_confirmation_token(
            self,
            email_confirmation_token: UserEmailConfirmationToken | None,
            now: datetime,
    ) -> UserEmailConfirmationToken:
        """
        Valida se um token de confirmação de e-mail pode ser utilizado.

        Args:
            email_confirmation_token: Token de confirmação localizado
                no repositório.
            now: Data e hora utilizada como referência para validação.

        Returns:
            Token de confirmação de e-mail validado.

        Raises:
            UserInvalidEmailConfirmationTokenError: Caso o token não exista,
                esteja expirado, já tenha sido utilizado ou tenha sido
                revogado.
        """

        if email_confirmation_token is None:
            raise UserInvalidEmailConfirmationTokenError(
                'Email confirmation token is invalid.'
            )

        if email_confirmation_token.used_at is not None:
            raise UserInvalidEmailConfirmationTokenError(
                'Email confirmation token has already been used.'
            )

        if email_confirmation_token.revoked_at is not None:
            raise UserInvalidEmailConfirmationTokenError(
                'Email confirmation token has been revoked.'
            )

        if email_confirmation_token.expires_at <= now:
            raise UserInvalidEmailConfirmationTokenError(
                'Email confirmation token has expired.'
            )

        return email_confirmation_token


def get_user_service(
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
    user_password_service: UserPasswordService = Depends(
        get_user_password_service
    ),
    user_email_service: UserEmailService = Depends(
        get_user_email_service
    ),
    user_repository: UserRepository = Depends(
        get_user_repository
    ),
) -> UserService:
    """
    Monta o serviço de domínio de usuários para uso nas rotas.

    Args:
        unit_of_work: Unidade de trabalho responsável pelo 
            controle da transação.
        user_password_service: Serviço responsável pelas operações 
            de senha.
        user_email_service: Serviço responsável pelas notificações 
            de e-mail.
        user_repository: Repositório utilizado para persistência de 
            usuários.

    Returns:
        Instância de `UserService`.
    """

    return UserService(
        unit_of_work=unit_of_work,
        user_password_service=user_password_service,
        user_email_service=user_email_service,
        user_repository=user_repository,
    )