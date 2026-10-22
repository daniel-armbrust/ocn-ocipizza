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
             body_html: str,
             body_text: str | None = None) -> None:
        """
        Envia um e-mail para o destinatário informado.

        Args:
            recipient: Endereço de e-mail do destinatário.
            subject: Assunto do e-mail.
            body_html: Conteúdo do e-mail em HTML.
            body_text: Conteúdo opcional do e-mail em texto simples.
        """
        pass
