#
# clients/smtp_email_sender.py
#

import smtplib
import ssl
from email.message import EmailMessage

from app.clients.email_sender import EmailSender


class SmtpEmailSender(EmailSender):
    """
    Implementa o envio de e-mails utilizando o protocolo SMTP.
    """

    def __init__(self,
                 host: str,
                 port: int,
                 sender: str,
                 username: str | None = None,
                 password: str | None = None,
                 use_tls: bool = False,
                 use_ssl: bool = False):
        """
        Inicializa o cliente responsável pelo envio de e-mails via SMTP.

        Args:
            host: Host do servidor SMTP.
            port: Porta utilizada para conexão com o servidor SMTP.
            sender: Endereço de e-mail utilizado como remetente.
            username: Usuário utilizado para autenticação SMTP.
            password: Senha utilizada para autenticação SMTP.
            use_tls: Indica se a conexão deve utilizar STARTTLS.
            use_ssl: Indica se a conexão deve utilizar SSL desde o início.
        """

        self.host = host
        self.port = port
        self.sender = sender
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.use_ssl = use_ssl

    def send(self,
             recipient: str,
             subject: str,
             body_html: str,
             body_text: str | None = None) -> None:
        """
        Envia um e-mail utilizando o servidor SMTP configurado.

        Args:
            recipient: Endereço de e-mail do destinatário.
            subject: Assunto do e-mail.
            body_html: Conteúdo opcional do e-mail em HTML.

        Raises:
            smtplib.SMTPException: Quando ocorre erro durante o envio
                ou autenticação no servidor SMTP.
        """

        # Cria a mensagem utilizando a implementação de e-mail
        # disponível na biblioteca padrão do Python.
        message = EmailMessage()

        message['From'] = self.sender
        message['To'] = recipient
        message['Subject'] = subject

        message.set_content(body_html, subtype='html')

        # Cria o contexto SSL utilizado pelas conexões SMTP seguras.
        ssl_context = ssl.create_default_context()

        if self.use_ssl:
            # SMTP_SSL estabelece uma conexão criptografada desde o início,
            # normalmente utilizada por servidores configurados na porta 465.
            with smtplib.SMTP_SSL(
                host=self.host,
                port=self.port,
                context=ssl_context
            ) as smtp:
                self._authenticate(smtp)
                smtp.send_message(message)

            return

        # Cria uma conexão SMTP convencional. Essa conexão pode ser usada
        # sem criptografia em desenvolvimento, como no Mailpit, ou ser
        # promovida para TLS por meio do comando STARTTLS.
        with smtplib.SMTP(host=self.host, port=self.port) as smtp:
            if self.use_tls:
                # STARTTLS transforma a conexão SMTP existente em uma
                # conexão criptografada antes da autenticação.
                smtp.starttls(context=ssl_context)

            self._authenticate(smtp)

            # Envia a mensagem já construída para o servidor SMTP.
            smtp.send_message(message)

    def _authenticate(self, smtp: smtplib.SMTP) -> None:
        """
        Realiza a autenticação no servidor SMTP quando necessária.

        Args:
            smtp: Conexão SMTP utilizada para realizar a autenticação.

        Raises:
            smtplib.SMTPException: Quando ocorre erro durante
                a autenticação SMTP.
        """

        # Servidores locais de desenvolvimento, como Mailpit, normalmente
        # não exigem autenticação. O login só é realizado quando usuário
        # e senha estiverem configurados.
        if self.username and self.password:
            smtp.login(self.username, self.password)