#
# services/notification_service.py
#

from fastapi import Depends

from app.services.email_service import (
    EmailService,
    get_email_service
)

from app.services.email_template_service import (
    EmailTemplateService,
    get_email_template_service
)
    
class NotificationService: 
    """ 
    Implementa o processamento das notificações recebidas da fila. 
    """
    
    def __init__(self, 
                 email_template_service: EmailTemplateService, 
                 email_service: EmailService): 
        """ 
        Inicializa o serviço responsável pelo processamento das notificações. 
        
        Args: 
            email_template_service: Serviço responsável por construir o 
                conteúdo dos e-mails a partir dos templates. 
            email_service: Serviço responsável pelo envio dos e-mails. 
        """ 
        
        self.email_template_service = email_template_service 
        self.email_service = email_service 
        
    def process(self, message: dict) -> None:
        """
        Processa uma mensagem de notificação recebida da fila.

        Args:
            message: Mensagem contendo o tipo da notificação, o destinatário
                e os dados utilizados para construção do conteúdo.

        Raises:
            ValueError: Quando a mensagem recebida não contém os campos
                obrigatórios para o processamento.
        """

        # Obtém as informações necessárias para identificar a notificação
        # e o destinatário que receberá o e-mail.
        notification_type = message.get('type')
        recipient = message.get('recipient')

        if not notification_type:
            raise ValueError('Notification type is required.')

        if not recipient:
            raise ValueError('Notification recipient is required.')

        # Remove os campos de controle da mensagem e mantém somente
        # os dados que serão utilizados na construção do template.
        data = {
            key: value
            for key, value in message.items()
            if key not in ('type', 'recipient')
        }

        # Seleciona o template correspondente ao tipo da notificação
        # e preenche seu conteúdo com os dados recebidos da fila.
        email = self.email_template_service.render(
            notification_type=notification_type,
            data=data
        )

        # Envia o e-mail somente depois que o conteúdo for construído
        # pelo serviço responsável pelos templates.
        self.email_service.send(
            recipient=recipient,
            subject=email['subject'],
            body_html=email['body_html']
        )


def get_notification_service() -> NotificationService:
    """
    Obtém o serviço responsável pelo processamento das notificações.

    Returns:
        Serviço configurado para processar as notificações recebidas.
    """
    
    return NotificationService(
        email_template_service=get_email_template_service(),
        email_service=get_email_service()
    )