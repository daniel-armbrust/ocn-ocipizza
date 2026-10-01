#
# services/user_email_service.py
#

from datetime import timedelta

from fastapi import Depends

from app.services.token_service import TokenService, get_token_service

from app.utils.utils import now_utc

from app.models.user import User
from app.models.email_confirmation_token import EmailConfirmationToken

from app.messaging.message_publisher import MessagePublisher
from app.dependencies.messaging import get_message_publisher

from app.repositories.email_confirmation_token_repository import EmailConfirmationTokenRepository
from app.dependencies.database import get_email_confirmation_token_repository

from app.exceptions.user_exceptions import UserEmailPublishError
from app.messaging.exceptions import MessagePublishError


class UserEmailService:
    """
    Serviço responsável pelos fluxos de comunicação por e-mail
    relacionados aos usuários.

    Esta camada coordena operações como confirmação de cadastro,
    redefinição de senha e notificações relacionadas à alteração
    de credenciais.

    O serviço não realiza o envio direto de e-mails e não possui
    conhecimento sobre servidores SMTP ou provedores de e-mail.
    Sua responsabilidade é gerar os dados necessários, persistir
    informações auxiliares quando necessário e publicar mensagens
    no mecanismo de mensageria para que o notification-service
    realize o processamento e envio da comunicação.

    As operações de persistência utilizam repositories através de
    abstrações, mantendo o serviço independente da tecnologia de
    armazenamento utilizada.

    A responsabilidade transacional não pertence a este serviço.
    O controle de commit e rollback é realizado pelo serviço que
    coordena o caso de uso através do UnitOfWork.
    """

    def __init__(self,
                 message_publisher: MessagePublisher,
                 email_confirmation_token_repository: EmailConfirmationTokenRepository,
                 token_service: TokenService
                 ) -> None:
        """
        Inicializa o serviço de e-mail do usuário. 
        
        Args:
            message_publisher: Publicador utilizado para enviar mensagens
                para a fila de notificações.
            email_confirmation_token_repository: Repositório utilizado para
                persistir e consultar tokens de confirmação de e-mail.
            token_service: Serviço responsável pela geração e criação do hash
                dos tokens
        """ 

        self.message_publisher = message_publisher
        self.email_confirmation_token_repository = email_confirmation_token_repository
        self.token_service = token_service

    def publish_confirmation_email(self, user: User) -> None:
        """
        Publica uma solicitação de envio do e-mail de confirmação de cadastro.

        A transação não é controlada por este serviço. O `UserEmailService` participa
        da transação iniciada pelo caso de uso que o chamou, mas não é responsável
        por executar commit ou rollback.

        O controle transacional pertence ao `UserService` através do `UnitOfWork`,
        garantindo que a criação do usuário, persistência do token e publicação
        da mensagem sejam confirmadas ou revertidas como uma única operação.

        Args:
            user: Usuário que receberá o e-mail de confirmação.

        Returns:
            None.

        Raises:
            UserEmailPublishError: Caso não seja possível publicar a mensagem
                na fila de notificações.
        """

        now = now_utc()

        # Gera o token original que será enviado ao usuário através do e-mail.
        # Este valor nunca deve ser armazenado no banco de dados.
        token = self.token_service.generate_token()

        # Gera o hash do token para armazenamento seguro.
        # Apenas o hash é persistido para permitir a validação posterior
        # sem expor o token original no banco.
        token_hash = self.token_service.hash_token(token)

        confirmation_token = EmailConfirmationToken(
            id=None,
            user_id=user.id,
            token_hash=token_hash,
            created_at=now,
            expires_at=now + timedelta(hours=24)
        )

        # Persiste o hash do token dentro da transação atual.
        # O UserService é o responsável pelo controle da transação através
        # do UnitOfWork.
        self.email_confirmation_token_repository.create(confirmation_token)

        # TODO: documentar USER_CONFIRMATION
        payload = {
            'type': 'USER_CONFIRMATION',
            'recipient': user.email,
            'full_name': user.full_name,
            'token': token
        }

        try:
            # Publica a mensagem na fila para que o notification-service
            # realize o envio do e-mail através do provedor SMTP.
            self.message_publisher.publish(payload)
        except MessagePublishError as ex:
            raise UserEmailPublishError(
                'Unable to publish confirmation email notification.'
            ) from ex

    def publish_password_reset_email(self, user: User, token: str) -> None:
        """
        Publica uma solicitação de envio do e-mail de redefinição de senha. 
        
        A mensagem é enviada para a fila de notificações e será processada 
        posteriormente pelo `notification-service`. 
        
        Args: 
            user: Usuário que receberá o e-mail de redefinição de senha. 
            token: Token temporário enviado ao usuário para autorizar a
                redefinição da senha.
        
        Returns: 
            None.

        Raises: 
            UserEmailPublishError: Caso não seja possível publicar a mensagem
                na fila de notificações.

            SQLAlchemyError: Caso ocorra uma falha ao persistir o token.
        """

        payload = {
            'type': 'PASSWORD_RESET',
            'recipient': user.email,
            'full_name': user.full_name,
            'token': token
        }

        try:
            self.message_publisher.publish(payload)
        except MessagePublishError as ex:
            raise UserEmailPublishError(
                'Unable to publish password reset email notification.'
            ) from ex

    def publish_password_change_email(self, user: User) -> None:
        """
        Publica uma solicitação de envio do e-mail informando que a 
        alteração da senha foi realizada com sucesso.

        Args:
            user: Usuário que receberá a notificação de alteração de senha.

        Returns:
            None.
        """
        pass


def get_user_email_service(
        message_publisher: MessagePublisher = Depends(
            get_message_publisher
        ),
        email_confirmation_token_repository: EmailConfirmationTokenRepository = Depends(
            get_email_confirmation_token_repository
        ),
        token_service: TokenService = Depends(get_token_service)
) -> UserEmailService:
    """
    Monta o serviço responsável pelos fluxos de e-mail relacionados
    ao usuário.

    Args:
        message_publisher: Publicador utilizado para enviar mensagens
            para a fila de notificações.
        email_confirmation_token_repository: Repositório utilizado para
            persistência dos tokens de confirmação de e-mail.
        token_service: Serviço responsável pela geração e criação do hash
            dos tokens

    Returns:
        Instância de `UserEmailService`.

    Raises:
        ValueError: Caso não exista uma implementação suportada para
            alguma dependência necessária.
    """
     
    return UserEmailService(
        message_publisher=message_publisher,
        email_confirmation_token_repository=email_confirmation_token_repository,
        token_service=token_service
    )
