#
# fn-password-recovery-email/modules/email.py
#

import os
import urllib.parse
import smtplib

from oci.auth import signers as oci_signers
from oci.email_data_plane import EmailDPClient
from oci.email_data_plane.models import Sender, Recipients, SubmitEmailDetails, \
    EmailAddress

# Globals
ENV = os.environ.get('ENV')
EMAIL_COMPARTMENT_OCID = os.environ.get('EMAIL_COMPARTMENT_OCID')
SMTP_IP = os.environ.get('SMTP_IP', '127.0.0.1')
SMTP_PORT = os.environ.get('SMTP_PORT', 8025)
HTTP_PORT = os.environ.get('HTTP_PORT', 5000)
HTTP_IP = os.environ.get('HTTP_IP', '127.0.0.1')

class Email():
    @property
    def address(self):
        return self.__address
    
    @address.setter
    def address(self, value: str):
        self.__address = value
    
    @property
    def token(self):
        return self.__token
    
    @token.setter
    def token(self, value: str):
        self.__token = value

    def __init__(self):
        if ENV == 'development':
            pass
        else:
            signer = oci_signers.get_resource_principals_signer()        
            self.__email_client = EmailDPClient(config={}, signer=signer)
    
    def __get_html_email(self):
        """Retorna o HTML que inclui o link que o usuário deve utilizar 
        para redefinir sua senha."""

        email_encoded = urllib.parse.quote(f'{self.__address}')
        token_encoded = urllib.parse.quote(f'{self.__token}')       

        if ENV == 'development':
            url_prefix = f'http://{HTTP_IP}:{HTTP_PORT}'
        else:
            url_prefix = 'https://www.ocipizza.com.br'

        url = f'{url_prefix}/user/new/password/form?e={email_encoded}&t={token_encoded}'

        html_email = f'''
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head></head>
            <body>
               <h1><a href="{url}">Clique no link para definir uma nova senha.</a></h1>
            </body>
            </html>
        '''

        return html_email
    
    def send(self):
        """Envia o e-mail para o usuário."""
        html_email = self.__get_html_email()

        if ENV == 'development':
            smtp_server = smtplib.SMTP(SMTP_IP, SMTP_PORT)

            smtp_server.sendmail(
                f'{self.__address}', 
                [f'no-reply@ocipizza.com.br'], 
                html_email
            )

            smtp_server.quit()

            return True
        else:
            email_from = EmailAddress(
                email='no-reply@ocipizza.com.br', 
                name='no-reply@ocipizza.com.br'
            )

            sender = Sender(
                compartment_id=EMAIL_COMPARTMENT_OCID,
                sender_address=email_from
            )

            email_to = EmailAddress(email=self.__address)

            recipients = Recipients(to=[email_to])
                    
            email_details = SubmitEmailDetails(
                subject='OCI Pizza - Recuperação de senha.',            
                body_html=html_email,
                sender=sender,
                recipients=recipients
            )

            resp = self.__email_client.submit_email(
                submit_email_details=email_details
            )

            if resp.status == 200:
                return True
            else:
                return False
