#
# clients/oci_email_sender.py
#

import oci

from app.clients.email_sender import EmailSender

from app.config.settings import settings

class OciEmailSender(EmailSender):
    """
    Implementa o envio de e-mails utilizando o OCI Email Delivery
    por meio do OCI SDK.
    """

    def __init__(self,
                 client: oci.email_data_plane.EmailDPClient,
                 compartment_id: str,
                 sender_email: str,
                 sender_name: str):
        """
        Inicializa o cliente responsável pelo envio de e-mails
        utilizando o OCI Email Delivery.

        Args:
            client: Cliente do OCI Email Delivery utilizado para
                submissão dos e-mails.
            compartment_id: OCID do compartment utilizado pelo serviço
                OCI Email Delivery.
            sender_email: Endereço de e-mail aprovado utilizado
                como remetente.
            sender_name: Nome apresentado como remetente do e-mail.
        """

        self.client = client
        self.compartment_id = compartment_id
        self.sender_email = sender_email
        self.sender_name = sender_name

    def send(self,
             recipient: str,
             subject: str,
             body_html: str,
             body_text: str | None = None) -> None:
        """
        Envia um e-mail em formato HTML utilizando o OCI Email Delivery.

        Args:
            recipient: Endereço de e-mail do destinatário.
            subject: Assunto do e-mail.
            body_html: Conteúdo HTML do e-mail.
            body_text: Conteúdo opcional em texto simples.
        """

        # Define o remetente utilizando um endereço previamente
        # aprovado no serviço OCI Email Delivery.
        sender = oci.email_data_plane.models.Sender(
            sender_address=oci.email_data_plane.models.EmailAddress(
                email=self.sender_email,
                name=self.sender_name
            ),
            compartment_id=self.compartment_id
        )

        # Define a lista de destinatários que receberão a mensagem.
        recipients = oci.email_data_plane.models.Recipients(
            to=[
                oci.email_data_plane.models.EmailAddress(
                    email=recipient
                )
            ]
        )

        # Monta os dados exigidos pelo OCI Email Delivery para
        # submissão da mensagem em formato HTML.
        email_details = (
            oci.email_data_plane.models.SubmitEmailDetails(
                sender=sender,
                recipients=recipients,
                subject=subject,
                body_html=body_html,
                body_text=body_text
            )
        )

        # Submete o e-mail ao OCI Email Delivery por meio da API
        # disponibilizada pelo data plane do serviço.
        self.client.submit_email(
            submit_email_details=email_details
        )
