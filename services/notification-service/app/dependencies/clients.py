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

    A região é identificada a partir do profile OCI ou automaticamente
    pela Compute Instance, conforme a estratégia de autenticação configurada.

    Returns:
        Cliente configurado para envio de e-mails por meio do OCI Email Delivery.

    Raises:
        ValueError: Quando alguma configuração obrigatória não estiver
            definida ou o modo de autenticação não for suportado.
    """

    # Utiliza o arquivo de configuração OCI para autenticação,
    # normalmente durante a execução local da aplicação.
    if settings.oci_auth_mode == 'config_file':
        
        config = oci.config.from_file(
            file_location=settings.oci_config_file,
            profile_name=settings.oci_config_profile
        )

        # Obtém a região a partir do arquivo de configuração.
        config['region'] = settings.oci_region

        return oci.email_data_plane.EmailDPClient(config=config)

    elif settings.oci_auth_mode == 'instance_principal':
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()

        # Obtém a região automaticamente com base na localidade 
        # em que a aplicação está sendo executada no OCI.
        region = signer.region

        if not region:
            raise ValueError(
                'Unable to determine OCI region '
                'from Instance Principal.'
            )

        return oci.email_data_plane.EmailDPClient(
            config={'region': region},
            signer=signer
        )

    raise ValueError(
        'Unsupported OCI authentication mode: '
        f'{settings.oci_auth_mode}'
    )