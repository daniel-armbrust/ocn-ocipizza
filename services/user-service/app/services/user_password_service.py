#
# services/user_password_service.py
#

import hashlib
import hmac
import secrets
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import Depends

from app.utils.utils import now_utc, normalize_email

from app.repositories.user_repository import UserRepository
from app.dependencies.database import get_user_repository

from app.repositories.password_reset_token_repository import PasswordResetTokenRepository
from app.dependencies.database import get_password_reset_token_repository

from app.repositories.password_history_repository import PasswordHistoryRepository
from app.dependencies.database import get_password_history_repository

from app.repositories.unit_of_work import UnitOfWork
from app.dependencies.database import get_unit_of_work

from app.services.token_service import TokenService, get_token_service
from app.services.user_email_service import UserEmailService, get_user_email_service

from app.models.password_reset_token import PasswordResetToken

from app.exceptions.user_exceptions import (
    UserUpdateError,
    UserNotFoundError,
    UserNotConfirmedError
)

from app.exceptions.user_password_exceptions import (
    UserInvalidPasswordError,
    UserPasswordMismatchError,
    UserPasswordResetError,
    UserInvalidPasswordResetTokenError
)


class UserPasswordService:
    """
    Serviço responsável pelas operações relacionadas à senha dos usuários.

    Esta camada concentra tanto operações específicas de senha, como geração
    e validação de hashes, quanto casos de uso relacionados à alteração e
    recuperação de senha.

    O serviço utiliza os repositories necessários para acessar e persistir
    informações relacionadas ao usuário, histórico de senhas e tokens de
    recuperação.

    O controle transacional das operações de alteração e recuperação de senha
    é realizado através do UnitOfWork.
    """
    
    def __init__(self,
                 user_repository: UserRepository,
                 password_reset_token_repository: PasswordResetTokenRepository,
                 #password_history_repository: PasswordHistoryRepository,
                 token_service: TokenService,
                 user_email_service: UserEmailService,
                 unit_of_work: UnitOfWork
    ) -> None:
        """
        Inicializa o serviço responsável pelas operações relacionadas
        à senha dos usuários.

        Args:
            user_repository: Repositório utilizado para consultar e atualizar
                os dados dos usuários.
            password_reset_token_repository: Repositório utilizado para
                persistir e consultar tokens de redefinição de senha.
            password_history_repository: Repositório utilizado para persistir
                o histórico de senhas dos usuários.
            token_service: Serviço responsável pela geração e criação do hash
                dos tokens utilizados nos fluxos de recuperação de senha.
            user_email_service: Serviço responsável por coordenar a publicação das
                notificações relacionadas à recuperação de senha.
            unit_of_work: Unidade de trabalho responsável pelo controle
                transacional das operações de persistência.

        Returns:
            None.
        """
        self.user_repository = user_repository
        self.password_reset_token_repository = password_reset_token_repository
        #self.password_history_repository = password_history_repository
        self.token_service = token_service
        self.user_email_service = user_email_service
        self.unit_of_work = unit_of_work

    def hash_password(self, password: str) -> str:
        """
        Gera hash seguro de senha usando PBKDF2-SHA256 e salt aleatório.

        Args:
            password: Senha em texto puro recebida no cadastro.

        Returns:
            String serializada contendo algoritmo, iterações, salt e digest.
        """
        salt = secrets.token_hex(16)

        iterations = 600000

        digest = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            iterations
        ).hex()

        return f'pbkdf2_sha256${iterations}${salt}${digest}'

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Valida uma senha em texto puro contra hash PBKDF2-SHA256 armazenado.

        Args:
            password: Senha em texto puro enviada no login.
            password_hash: Hash armazenado no repositório de usuários.

        Returns:
            `True` quando a senha corresponde ao hash armazenado.
        """

        try:
            algorithm, iterations, salt, digest = password_hash.split('$', 3)
        except ValueError:
            return False

        if algorithm != 'pbkdf2_sha256':
            return False

        computed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            int(iterations)
        ).hex()

        return hmac.compare_digest(computed, digest)

    def validate_password_confirmation(self,
                                       new_password: str,
                                       confirm_new_password: str) -> None:
        """
        Valida se a nova senha e sua confirmação possuem o mesmo valor.

        Args:
            new_password: Nova senha informada pelo usuário.
            confirm_new_password: Confirmação da nova senha.

        Returns:
            None.

        Raises:
            UserPasswordMismatchError: Caso a nova senha e sua confirmação
                sejam diferentes.
        """

        if new_password != confirm_new_password:
            raise UserPasswordMismatchError(
                'New password confirmation does not match.'
            )

    def update_password(self,
                        user_id: UUID,
                        current_password: str,
                        new_password: str,
                        confirm_new_password: str) -> None:
            """
            Atualiza a senha do usuário autenticado.

            Este caso de uso exige que o usuário informe sua senha atual antes
            de permitir a alteração. A nova senha também deve ser confirmada
            para evitar erros de digitação.

            Antes da atualização, o hash da senha atual é armazenado no histórico
            de senhas do usuário.

            Args:
                user_id: Identificador UUID do usuário.
                current_password: Senha atual informada pelo usuário.
                new_password: Nova senha desejada pelo usuário.
                confirm_new_password: Confirmação da nova senha.

            Returns:
                None.

            Raises:
                UserNotFoundError: Caso o usuário não seja encontrado.
                InvalidPasswordError: Caso a senha atual informada seja inválida.
                PasswordMismatchError: Caso a nova senha e sua confirmação
                    sejam diferentes.
                UserUpdateError: Caso ocorra uma falha durante a atualização
                    da senha.
            """
            # Localiza o usuário que terá a senha alterada.
            user = self.user_repository.get_by_id(user_id)

            if user is None:
                raise UserNotFoundError('User not found.')

            # A alteração de senha somente é permitida para usuários
            # que já concluíram a confirmação do endereço de e-mail.
            if not user.confirmed:
                raise UserNotConfirmedError('User email is not confirmed.')

            # Verifica se a nova senha e sua confirmação possuem
            # exatamente o mesmo valor.
            self.validate_password_confirmation(
                new_password,
                confirm_new_password
            )

            # Valida a senha atual antes de permitir a alteração.
            if not self.verify_password(
                current_password,
                user.password_hash
            ):
                raise UserInvalidPasswordError('Current password is invalid.')

            # Gera o hash da nova senha.
            user.password_hash = self.hash_password(new_password)

            # Atualiza a data da última modificação do usuário.
            user.updated_at = now_utc()

            try:
                # TODO: Histórico de Senhas
                # Registra o hash da senha atual antes de substituí-lo.

                # Persiste o novo estado do usuário.
                self.user_repository.update(user)

                self.unit_of_work.commit()
            except Exception as ex:
                self.unit_of_work.rollback()
                raise UserUpdateError('Error updating the user password.') from ex

    def request_password_reset(self, email: str) -> None:
        """
        Inicia o processo de redefinição da senha de um usuário.

        O usuário é localizado através do endereço de e-mail informado.
        Caso exista e esteja confirmado, um token temporário é gerado,
        seu hash é persistido e o token original é enviado para o
        `notification-service` através do mecanismo de mensageria.

        Por segurança, a ausência de um usuário associado ao e-mail
        informado não gera erro. Dessa forma, a API pode retornar uma
        resposta genérica sem revelar se o endereço está cadastrado.

        Args:
            email: Endereço de e-mail utilizado para localizar o usuário.

        Returns:
            None.

        Raises:
            UserNotConfirmedError: Caso o usuário exista, mas ainda não
                tenha confirmado seu endereço de e-mail.
            UserPasswordResetError: Caso ocorra uma falha durante a
                persistência do token ou publicação da mensagem.
        """

        # Localiza o usuário através do endereço de e-mail informado.
        user = self.user_repository.get_by_email(normalize_email(email))

        # Não informa ao consumidor da API se o endereço de e-mail
        # está ou não cadastrado, evitando enumeração de usuários.
        if user is None:
            return

        # O processo de recuperação de senha somente pode ser iniciado
        # para usuários que já confirmaram o endereço de e-mail.
        if not user.confirmed:
            raise UserNotConfirmedError('User email is not confirmed.')

        # Gera o token original que será enviado ao usuário.
        # O token original nunca deve ser armazenado no banco de dados.
        token = self.token_service.generate_token()

        # Apenas o hash do token é persistido.
        token_hash = self.token_service.hash_token(token)

        now = now_utc()

        # Cria o modelo que representa o token de redefinição de senha.
        password_reset_token = PasswordResetToken(
            id=None,
            user_id=user.id,
            token_hash=token_hash,
            created_at=now,
            expires_at=now + timedelta(hours=1)
        )

        try:
            # Persiste o token de recuperação dentro da transação atual.
            self.password_reset_token_repository.create(password_reset_token)

            # Publica a solicitação para que o notification-service
            # realize o envio do e-mail de recuperação de senha.
            self.user_email_service.publish_password_reset_email(
                user=user,
                token=token
            )

            self.unit_of_work.commit()
        except Exception as ex:
            self.unit_of_work.rollback()
            raise UserPasswordResetError('Error requesting password reset.') from ex

    def reset_password(self, 
                       token: str,
                       new_password: str, 
                       confirm_new_password: str) -> None:
        """
        Redefine a senha de um usuário utilizando um token de recuperação.

        Este caso de uso é utilizado quando o usuário não conhece sua senha
        atual. A autorização para alteração da senha é realizada através do
        token temporário enviado previamente ao endereço de e-mail associado
        à conta.

        Args:
            token: Token de redefinição de senha recebido pelo usuário.
            new_password: Nova senha desejada pelo usuário.
            confirm_new_password: Confirmação da nova senha.

        Returns:
            None.

        Raises:
            PasswordMismatchError: Caso a nova senha e sua confirmação
                sejam diferentes.
            UserInvalidPasswordResetTokenError: Caso o token seja inválido,
                expirado, já utilizado ou revogado.
            UserNotFoundError: Caso o usuário associado ao token não
                seja encontrado.
            UserNotConfirmedError: Caso o usuário ainda não tenha confirmado
                seu endereço de e-mail.
            UserPasswordResetError: Caso ocorra uma falha durante a consulta
                ou persistência dos dados necessários à redefinição da senha.
        """

        # Verifica se a nova senha e sua confirmação possuem exatamente 
        # o mesmo valor.
        self.validate_password_confirmation(
            new_password,
            confirm_new_password
        )

        # Gera o hash do token recebido.
        token_hash = self.token_service.hash_token(token)

        try:
            # Localiza o registro correspondente ao token informado.
            password_reset_token = (
                self.password_reset_token_repository.get_by_hash(
                    token_hash
                )
            )
        except Exception as ex:
            raise UserPasswordResetError(
                'Error retrieving password reset token.'
            ) from ex

        now = now_utc()

        # Valida se o token existe e se ainda pode ser utilizado.
        self._validate_password_reset_token(password_reset_token, now)

        try:
            # Localiza o usuário associado ao token de redefinição.
            user = self.user_repository.get_by_id(password_reset_token.user_id)
        except Exception as ex:
            raise UserPasswordResetError(
                'Error retrieving user for password reset.'
            ) from ex

        if user is None:
            raise UserNotFoundError('User not found.')

        # A redefinição de senha somente é permitida para usuários
        # que já confirmaram seu endereço de e-mail.
        if not user.confirmed:
            raise UserNotConfirmedError('User email is not confirmed.')

        # Gera o hash da nova senha.
        user.password_hash = self.hash_password(new_password)

        # Atualiza a data da última modificação do usuário.
        user.updated_at = now

        try:
            # TODO: Registrar o hash da senha anterior no histórico.

            # Persiste o novo hash da senha do usuário.
            self.user_repository.update(user)

            # Marca o token como utilizado para impedir sua reutilização.
            self.password_reset_token_repository.mark_as_used(
                password_reset_token.id,
                now
            )

            self.unit_of_work.commit()
        except Exception as ex:
            self.unit_of_work.rollback()
            raise UserPasswordResetError(
                'Error resetting the user password.'
            ) from ex

    def _validate_password_reset_token(self,
                                       password_reset_token: PasswordResetToken | None,
                                       now: datetime) -> None:
        """
        Valida se um token de redefinição de senha pode ser utilizado.

        Args:
            password_reset_token: Token de redefinição localizado no repositório.
            now: Data e hora utilizada como referência para validação.

        Returns:
            None.

        Raises:
            UserInvalidPasswordResetTokenError: Caso o token não exista, esteja
                expirado, já tenha sido utilizado ou tenha sido revogado.
        """

        if password_reset_token is None:
            raise UserInvalidPasswordResetTokenError(
                'Password reset token is invalid.'
            )

        if password_reset_token.used_at is not None:
            raise UserInvalidPasswordResetTokenError(
                'Password reset token has already been used.'
            )

        if password_reset_token.revoked_at is not None:
            raise UserInvalidPasswordResetTokenError(
                'Password reset token has been revoked.'
            )

        if password_reset_token.expires_at <= now:
            raise UserInvalidPasswordResetTokenError(
                'Password reset token has expired.'
            )


def get_user_password_service(
        user_repository: UserRepository = Depends(
            get_user_repository
        ),
        password_reset_token_repository: PasswordResetTokenRepository = Depends(
            get_password_reset_token_repository
        ),
        #password_history_repository: PasswordHistoryRepository = Depends(
        #    get_password_history_repository
        #),
        token_service: TokenService = Depends(
            get_token_service
        ),
        user_email_service: UserEmailService = Depends(
            get_user_email_service
        ),
        unit_of_work: UnitOfWork = Depends(
            get_unit_of_work
        )
) -> UserPasswordService:
    """
    Monta o serviço responsável pelas operações relacionadas à senha
    dos usuários.

    Args:
        user_repository: Repositório utilizado para consulta e atualização
            dos usuários.
        password_reset_token_repository: Repositório utilizado para
            persistência dos tokens de redefinição de senha.
        password_history_repository: Repositório utilizado para armazenar
            o histórico de senhas dos usuários.
        token_service: Serviço responsável pela geração e hash dos tokens.
        user_email_service: Serviço responsável pela comunicação de eventos
            relacionados ao envio de e-mails.
        unit_of_work: Unidade de trabalho utilizada para controle transacional.

    Returns:
        Instância de `UserPasswordService`.
    """

    return UserPasswordService(
        user_repository=user_repository,
        password_reset_token_repository=password_reset_token_repository,
        #password_history_repository=password_history_repository,
        token_service=token_service,
        user_email_service=user_email_service,
        unit_of_work=unit_of_work,
    )
