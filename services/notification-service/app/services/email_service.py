#
# services/email_service.py
#

from app.clients.email_sender import EmailSender
from app.dependencies.clients import get_email_sender

class EmailService:
    """
    Implementa as operações relacionadas ao envio de e-mails.
    """

    def __init__(self, email_sender: EmailSender):
        """
        Inicializa o serviço responsável pelo envio de e-mails.

        Args:
            email_sender: Implementação utilizada para realizar
                o envio dos e-mails.
        """

        self.email_sender = email_sender

    def send(self, 
             recipient: str, 
             subject: str,   
             body_html: str,
             body_text: str | None = None) -> None:
        """
        Envia um e-mail para o destinatário informado.

        Args:
            recipient: Endereço de e-mail do destinatário.
            subject: Assunto do e-mail.
            body_text: Conteúdo do e-mail em texto simples.
            body_html: Conteúdo opcional do e-mail em HTML.
        """
        
        self.email_sender.send(
            recipient=recipient,
            subject=subject,
            body_text=body_text,
            body_html=body_html
        )


def get_email_service() -> EmailService:
    """
    Obtém o serviço responsável pelo envio de e-mails.

    Args:
        email_sender: Implementação responsável pelo envio efetivo
            das mensagens de e-mail.

    Returns:
        Serviço responsável pelas operações de envio de e-mails.
    """
    
    return EmailService(
        email_sender=get_email_sender()
    )