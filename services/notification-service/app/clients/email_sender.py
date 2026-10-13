#
# clients/email_sender.py
#

from abc import ABC, abstractmethod

class EmailSender(ABC):
    """
    Define as operações necessárias para envio de e-mails.
    """

    @abstractmethod
    def send(self,
             recipient: str,
             subject: str,
             body_text: str,
             body_html: str | None = None) -> None:
        """
        Envia um e-mail para o destinatário informado.

        Args:
            recipient: Endereço de e-mail do destinatário.
            subject: Assunto do e-mail.
            body_text: Conteúdo do e-mail em texto simples.
            body_html: Conteúdo opcional do e-mail em HTML.
        """
        pass