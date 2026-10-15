#
# services/email_template_service.py
#

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from app.config.settings import settings
from app.notifications.email_templates import EMAIL_TEMPLATES
from app.services.order_email_template_service import (
    OrderEmailTemplateService
)
from app.services.user_email_template_service import (
    UserEmailTemplateService
)


class EmailTemplateService:
    """
    Coordena a seleção e a renderização dos templates de e-mail.

    A preparação dos dados é delegada ao serviço correspondente ao
    domínio da notificação.
    """

    def __init__(self) -> None:
        """Inicializa o renderizador e os preparadores por domínio."""

        self.environment = Environment(
            loader=FileSystemLoader(settings.email_templates_path),
            autoescape=True
        )

        user_service = UserEmailTemplateService()
        order_service = OrderEmailTemplateService()

        # Mantém a seleção dos preparadores centralizada sem misturar as
        # regras de e-mail de usuários com as regras de pedidos.
        self._data_preparers = {
            'USER_CONFIRMATION': user_service.prepare,
            'USER_PASSWORD_RESET': user_service.prepare,
            'ORDER_RECEIVED': order_service.prepare,
            'ORDER_UPDATED': order_service.prepare,
            'ORDER_SENT': order_service.prepare,
            'ORDER_DELIVERED': order_service.prepare
        }

    def render(self, notification_type: str, data: dict) -> dict:
        """
        Renderiza o conteúdo HTML de um e-mail.

        Args:
            notification_type: Tipo da notificação recebida.
            data: Dados utilizados para preencher o template.

        Returns:
            Dicionário contendo assunto e conteúdo HTML.

        Raises:
            ValueError: Quando o tipo ou template não estiver configurado.
        """

        template_config = EMAIL_TEMPLATES.get(notification_type)

        if not template_config:
            raise ValueError(
                f'Unsupported notification type: {notification_type}'
            )

        template_data = self._prepare_data(
            notification_type=notification_type,
            data=data
        )

        try:
            html_template = self.environment.get_template(
                template_config['html']
            )
        except TemplateNotFound as ex:
            raise ValueError(
                f'Email template not found: {ex.name}'
            ) from ex

        return {
            'subject': template_config['subject'],
            'body_html': html_template.render(**template_data)
        }

    def _prepare_data(self, notification_type: str, data: dict) -> dict:
        """
        Delega a preparação ao serviço do domínio correspondente.

        Args:
            notification_type: Tipo da notificação recebida.
            data: Dados originais da mensagem.

        Returns:
            Dados preparados para o template.

        Raises:
            ValueError: Quando o tipo não possuir preparador.
        """

        preparer = self._data_preparers.get(notification_type)

        if preparer is None:
            raise ValueError(
                f'Unsupported notification type: {notification_type}'
            )

        return preparer(
            notification_type=notification_type,
            data=data.copy()
        )


def get_email_template_service() -> EmailTemplateService:
    """Obtém o serviço responsável pela renderização dos e-mails."""

    return EmailTemplateService()
