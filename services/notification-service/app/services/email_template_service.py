#
# services/email_template_service.py
#

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from app.config.settings import settings
from app.notifications.email_templates import EMAIL_TEMPLATES

class EmailTemplateService:
    """
    Implementa a seleção e a renderização dos templates utilizados
    nas notificações por e-mail.
    """

    def __init__(self):
        """
        Inicializa o serviço responsável pelos templates de e-mail.
        """

        # Configura o Jinja2 para carregar os templates armazenados
        # no diretório definido para os e-mails da aplicação.
        self.environment = Environment(
            loader=FileSystemLoader(
                settings.email_templates_path
            ),
            autoescape=True
        )

        # Associa cada tipo de notificação ao método responsável por
        # preparar os dados específicos utilizados na renderização.
        self._data_preparers = {
            'USER_CONFIRMATION': self._prepare_user_confirmation_data,
            'USER_PASSWORD_RESET': self._prepare_user_password_reset_data,
            'USER_ORDER_SENT': self._prepare_user_order_sent_data
        }

    def render(self, notification_type: str, data: dict) -> dict:
        """
        Renderiza o conteúdo HTML de um e-mail a partir do tipo da notificação.

        Args:
            notification_type: Tipo da notificação recebida da fila.
            data: Dados utilizados para preencher o template.

        Returns:
            Dicionário contendo o assunto e o conteúdo HTML do e-mail.

        Raises:
            ValueError: Quando o tipo da notificação não possui template
                configurado ou quando o template não é encontrado.
        """

        # Obtém a configuração associada ao tipo da notificação recebida.
        template_config = EMAIL_TEMPLATES.get(
            notification_type
        )

        if not template_config:
            raise ValueError(
                f'Unsupported notification type: {notification_type}'
            )

        # Prepara os dados específicos do tipo da notificação antes
        # de disponibilizá-los para o template.
        template_data = self._prepare_data(
            notification_type=notification_type,
            data=data
        )

        try:
            # Carrega o template HTML configurado para o tipo
            # da notificação recebida.
            html_template = self.environment.get_template(
                template_config['html']
            )
        except TemplateNotFound as ex:
            raise ValueError(
                f'Email template not found: {ex.name}'
            ) from ex

        # Renderiza o conteúdo HTML utilizando os dados preparados
        # especificamente para o tipo da notificação.
        body_html = html_template.render(
            **template_data
        )

        return {
            'subject': template_config['subject'],
            'body_html': body_html
        }

    def _prepare_data(self, notification_type: str, data: dict) -> dict:
        """
        Prepara os dados utilizados para renderização do template.

        Args:
            notification_type: Tipo da notificação recebida.
            data: Dados originais recebidos na mensagem da fila.

        Returns:
            Dados preparados para utilização pelo template.
        """

        template_data = data.copy()

        preparer = self._data_preparers.get(
            notification_type
        )

        if preparer:
            return preparer(template_data)

        return template_data

    def _prepare_user_confirmation_data(self, data: dict) -> dict:
        """
        Prepara os dados utilizados no e-mail de confirmação do usuário.

        Args:
            data: Dados recebidos na mensagem de confirmação.

        Returns:
            Dados preparados para renderização do template.

        Raises:
            ValueError: Quando faltam dados obrigatórios para a notificação.
        """

        full_name = data.get('full_name')
        token = data.get('token')

        if not full_name or not token:
            raise ValueError(
                'Full name and token are required for USER_CONFIRMATION.'
            )

        # Constrói a URL utilizada pelo usuário para confirmar
        # o endereço de e-mail cadastrado.
        data['confirmation_url'] = (
            f'{settings.site_url}/users/confirm'
            f'?token={token}'
        )

        return data

    def _prepare_user_order_sent_data(self):
        pass

    def _prepare_user_password_reset_data(self):
        pass


def get_email_template_service() -> EmailTemplateService:
    """
    Obtém o serviço responsável pela construção dos templates de e-mail.

    Returns:
        Serviço responsável por selecionar e renderizar os templates
        utilizados nas notificações.
    """

    return EmailTemplateService()