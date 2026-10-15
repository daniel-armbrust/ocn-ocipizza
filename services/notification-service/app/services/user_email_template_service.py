#
# services/user_email_template_service.py
#

from app.config.settings import settings


class UserEmailTemplateService:
    """
    Prepara os dados dos templates de e-mail relacionados aos usuários.
    """

    def prepare(self, notification_type: str, data: dict) -> dict:
        """
        Prepara os dados de acordo com o tipo de notificação do usuário.

        Args:
            notification_type: Tipo da notificação recebida.
            data: Dados originais da mensagem.

        Returns:
            Dados validados e complementados para o template.

        Raises:
            ValueError: Quando faltarem dados obrigatórios.
        """

        if notification_type == 'USER_CONFIRMATION':
            return self._prepare_confirmation(data)

        if notification_type == 'USER_PASSWORD_RESET':
            return self._prepare_password_reset(data)

        raise ValueError(
            f'Unsupported user notification type: {notification_type}'
        )

    def _prepare_confirmation(self, data: dict) -> dict:
        """
        Prepara os dados do e-mail de confirmação do usuário.

        Args:
            data: Dados recebidos na mensagem de confirmação.

        Returns:
            Dados com a URL de confirmação.

        Raises:
            ValueError: Quando faltar nome ou token.
        """

        full_name = data.get('full_name')
        token = data.get('token')

        if not full_name or not token:
            raise ValueError(
                'Full name and token are required for USER_CONFIRMATION.'
            )

        data['confirmation_url'] = (
            f'{settings.site_url}/users/confirm'
            f'?token={token}'
        )

        return data

    def _prepare_password_reset(self, data: dict) -> dict:
        """
        Prepara os dados do e-mail de redefinição de senha.

        Args:
            data: Dados recebidos na mensagem de redefinição.

        Returns:
            Dados com a URL de redefinição.

        Raises:
            ValueError: Quando faltar nome ou token.
        """

        full_name = data.get('full_name')
        token = data.get('token')

        if not full_name or not token:
            raise ValueError(
                'Full name and token are required for USER_PASSWORD_RESET.'
            )

        data['password_reset_url'] = (
            f'{settings.site_url}/users/password-reset/confirm'
            f'?token={token}'
        )

        return data
