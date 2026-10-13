#
# dependencies/clients.py
#

import oci

from app.clients.email_sender import EmailSender
from app.clients.smtp_email_sender import SmtpEmailSender
from app.clients.oci_email_sender import OciEmailSender

from app.config.settings import settings

def get_email_sender() -> EmailSender:
    """
    Obtém a implementação responsável pelo envio de e-mails.

    Returns:
        Implementação configurada para realizar o envio dos e-mails.

    Raises:
        ValueError: Quando o provedor de e-mail configurado não é suportado.
    """

    # Utiliza SMTP para ambientes locais com Mailpit ou para
    # integração com o OCI Email Delivery através do protocolo SMTP.
    if settings.email_provider == 'smtp':
        return SmtpEmailSender(
            host=settings.smtp_host,
            port=settings.smtp_port,
            sender=settings.smtp_email_sender,
            username=settings.smtp_username,
            password=settings.smtp_password,
            use_tls=settings.smtp_use_tls
        )

    # Utiliza o OCI SDK quando o envio de e-mails for realizado
    # diretamente pela API do OCI Email Delivery.
    if settings.email_provider == 'oci':
        return OciEmailSender(
            client=get_oci_email_client(),
            compartment_id=settings.oci_email_delivery_compartment_id,
            sender_email=settings.smtp_email_sender,
            sender_name=settings.oci_email_sender_name
        )

    raise ValueError(
        f'Unsupported email provider: {settings.email_provider}'
    )


def get_oci_email_client() -> oci.email_data_plane.EmailDPClient: 
    """ 
    Obtém o cliente utilizado para comunicação com o OCI Email Delivery. 
    
    Returns: 
        Cliente configurado para envio de e-mails por meio do OCI Email Delivery. 
    """ 
    
    # Utiliza Instance Principal para autenticar o notification-service 
    # junto aos serviços OCI sem armazenar credenciais na aplicação. 
    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner() 
    
    # Cria o cliente do data plane responsável pela submissão #
    # dos e-mails ao OCI Email Delivery. 
    return oci.email_data_plane.EmailDPClient( 
        config={'region': settings.oci_region}, 
        signer=signer 
    )