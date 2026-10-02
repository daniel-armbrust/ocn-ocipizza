#
# services/user_authentication_service.py
#

from datetime import timedelta
from uuid import UUID

from fastapi import Depends

from app.config.settings import settings

from app.repositories.user_repository import UserRepository
from app.dependencies.database import get_user_repository
    
from app.repositories.user_refresh_token_repository import UserRefreshTokenRepository
from app.dependencies.database import get_user_refresh_token_repository

from app.services.token_service import TokenService
from app.dependencies.security import get_token_service

from app.services.user_password_service import UserPasswordService, get_user_password_service

from app.services.jwt_service import JwtService, get_jwt_service

from app.repositories.unit_of_work import UnitOfWork
from app.dependencies.database import get_unit_of_work

from app.models.user_authentication_tokens import UserAuthenticationTokens
from app.models.user_refresh_token import UserRefreshToken

from app.utils.utils import normalize_email, now_utc

from app.exceptions.user_exceptions import UserNotConfirmedError, UserNotFoundError
from app.exceptions.user_password_exceptions import UserInvalidPasswordError
from app.exceptions.user_authentication_exceptions import UserAuthenticationError


class UserAuthenticationService:
    """
    Serviço responsável pelos casos de uso relacionados
    à autenticação dos usuários.

    Esta camada coordena a validação das credenciais, geração dos
    access tokens JWT e criação dos refresh tokens utilizados para
    manutenção das sessões dos usuários.

    O serviço não implementa diretamente operações criptográficas
    relacionadas a senhas ou JWT. Essas responsabilidades são
    delegadas aos serviços especializados.
    """

    def __init__(
            self,
            user_repository: UserRepository,
            user_refresh_token_repository: UserRefreshTokenRepository,
            user_password_service: UserPasswordService,
            jwt_service: JwtService,
            token_service: TokenService,
            unit_of_work: UnitOfWork,
            refresh_token_expiration_days: int) -> None:
        """
        Inicializa o serviço responsável pela autenticação dos usuários.

        Args:
            user_repository: Repositório utilizado para consultar usuários.
            user_refresh_token_repository: Repositório utilizado para
                persistir e consultar refresh tokens.
            user_password_service: Serviço utilizado para validar
                as senhas dos usuários.
            jwt_service: Serviço responsável pela geração e validação
                dos access tokens JWT.
            token_service: Serviço responsável pela geração e criação
                do hash dos refresh tokens.
            unit_of_work: Unidade de trabalho responsável pelo controle
                transacional das operações de persistência.
            refresh_token_expiration_days: Tempo de validade dos refresh
                tokens, em dias.

        Returns:
            None.
        """

        self.user_repository = user_repository
        self.user_refresh_token_repository = user_refresh_token_repository
        self.user_password_service = user_password_service
        self.jwt_service = jwt_service
        self.token_service = token_service
        self.unit_of_work = unit_of_work
        self.refresh_token_expiration_days = refresh_token_expiration_days

    def login(self, email: str, password: str) -> UserAuthenticationTokens:
        """
        Autentica um usuário através de e-mail e senha.

        Após a validação das credenciais, um access token JWT e um
        refresh token são gerados. Apenas o hash do refresh token
        é persistido no banco de dados.

        Args:
            email: Endereço de e-mail utilizado para identificar
                o usuário.
            password: Senha informada para autenticação.

        Returns:
            Tokens gerados para a sessão autenticada do usuário.

        Raises:
            UserNotFoundError: Caso não exista usuário associado
                ao endereço de e-mail informado.
            UserInvalidPasswordError: Caso a senha informada não
                corresponda à senha armazenada.
            UserNotConfirmedError: Caso o usuário ainda não tenha
                confirmado seu endereço de e-mail.
            UserAuthenticationError: Caso ocorra uma falha durante
                o processo de autenticação ou persistência da sessão.
        """

        # Normaliza o endereço de e-mail antes de realizar
        # a consulta no repositório.
        normalized_email = normalize_email(email)

        try:
            user = self.user_repository.get_by_email(normalized_email)
        except Exception as ex:
            raise UserAuthenticationError(
                'Error retrieving user for authentication.'
            ) from ex

        # A rota deverá retornar uma mensagem genérica para não
        # revelar se o endereço de e-mail está cadastrado.
        if user is None:
            raise UserNotFoundError('User not found.')

        # Usuários que ainda não confirmaram o endereço de e-mail
        # não podem iniciar uma sessão autenticada.
        if not user.confirmed:
            raise UserNotConfirmedError('User email is not confirmed.')

        # Valida a senha informada utilizando o serviço responsável
        # pelas operações criptográficas relacionadas às senhas.
        if not self.user_password_service.verify_password(
            password,
            user.password_hash
        ):
            raise UserInvalidPasswordError('Invalid user password.')

        now = now_utc()

        try:
            # Cria o access token JWT assinado pelo user-service.
            access_token, expires_in = (
                self.jwt_service.create_access_token(
                    user_id=user.id,
                    is_admin=user.is_admin,
                )
            )

            # O refresh token é um valor aleatório independente
            # do access token JWT.
            refresh_token = self.token_service.generate_token()

            # Apenas o hash do refresh token será persistido.
            refresh_token_hash = self.token_service.hash_token(refresh_token)

            # Cria o modelo que representa a sessão persistida
            # através do refresh token.
            user_refresh_token = UserRefreshToken(
                id=None,
                user_id=user.id,
                token_hash=refresh_token_hash,
                created_at=now,
                expires_at=(now + timedelta(days=self.refresh_token_expiration_days))
            )

            # Persiste somente o hash do refresh token.
            self.user_refresh_token_repository.create(user_refresh_token)

            self.unit_of_work.commit()
        except Exception as ex:
            self.unit_of_work.rollback()
            raise UserAuthenticationError(
                'Error creating user authentication session.'
            ) from ex

        # O refresh token original é retornado somente ao cliente.
        # Ele nunca é persistido em texto puro.
        return UserAuthenticationTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in
        )

    def logout(self, refresh_token: str) -> None:
        """
        Encerra uma sessão através da revogação do refresh token.

        O refresh token recebido é convertido em hash e localizado
        no repositório. Caso seja válido, ele é marcado como revogado
        para impedir novas renovações do access token.

        Args:
            refresh_token: Refresh token associado à sessão que será
                encerrada.

        Returns:
            None.

        Raises:
            UserAuthenticationError: Caso ocorra uma falha durante
                o processo de encerramento da sessão.
        """

        # FIXME: Um detalhe importante: esse logout invalida a capacidade 
        # de renovar a sessão. O access token JWT que já foi emitido ainda 
        # funcionará até seus 15 minutos expirarem. Esse comportamento é 
        # uma consequência direta de termos escolhido JWT stateless para 
        # o access token.

        # Apenas o hash do refresh token é utilizado para realizar
        # consultas no banco de dados.
        token_hash = self.token_service.hash_token(refresh_token)

        try:
            # Localiza o refresh token correspondente ao valor
            # apresentado pelo cliente.
            stored_refresh_token = (
                self.user_refresh_token_repository.get_by_hash(token_hash)
            )

            # O logout é tratado de forma idempotente.
            # Caso o token não exista, nenhuma ação adicional
            # precisa ser realizada.
            if stored_refresh_token is None:
                return

            # Um token já revogado também não exige nova alteração.
            if stored_refresh_token.revoked_at is not None:
                return

            now = now_utc()

            # Marca o refresh token como revogado para impedir
            # sua utilização em futuras renovações de sessão.
            self.user_refresh_token_repository.revoke(
                stored_refresh_token.id,
                now
            )

            self.unit_of_work.commit()
        except Exception as ex:
            self.unit_of_work.rollback()
            raise UserAuthenticationError('Error logging out user.') from ex

    def revoke_user_sessions(self, user_id: UUID):
        pass


def get_user_authentication_service(
    user_repository: UserRepository = Depends(get_user_repository),
    user_refresh_token_repository: UserRefreshTokenRepository = Depends(
        get_user_refresh_token_repository
    ),
    user_password_service: UserPasswordService = Depends(
        get_user_password_service
    ),
    jwt_service: JwtService = Depends(get_jwt_service),
    token_service: TokenService = Depends(get_token_service),
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
    refresh_token_expiration_days=(
        settings.refresh_token_expiration_days
    )
) -> UserAuthenticationService:
    """
    Fornece o serviço responsável pelos casos de uso relacionados
    à autenticação dos usuários.

    Args:
        user_repository: Repositório utilizado para consultar usuários.
        user_refresh_token_repository: Repositório utilizado para
            persistir e consultar refresh tokens.
        user_password_service: Serviço utilizado para validar
            as senhas dos usuários.
        jwt_service: Serviço responsável pela geração e validação
            dos access tokens JWT.
        token_service: Serviço responsável pela geração e criação
            do hash dos refresh tokens.
        unit_of_work: Unidade de trabalho utilizada para controle
            transacional das operações de persistência.

    Returns:
        Instância de `UserAuthenticationService`.
    """

    return UserAuthenticationService(
        user_repository=user_repository,
        user_refresh_token_repository=user_refresh_token_repository,
        user_password_service=user_password_service,
        jwt_service=jwt_service,
        token_service=token_service,
        unit_of_work=unit_of_work,
        refresh_token_expiration_days=refresh_token_expiration_days
    )