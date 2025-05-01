#
# fn-password-recovery-email/modules/email.py
#

import os
import urllib.parse

from oci.auth import signers as oci_signers
from oci.email_data_plane import EmailDPClient
from oci.email_data_plane.models import Sender, Recipients, SubmitEmailDetails, \
    EmailAddress

# Globals
EMAIL_COMPARTMENT_OCID = os.environ.get('EMAIL_COMPARTMENT_OCID')
ENV = os.environ.get('ENV')

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
        signer = oci_signers.get_resource_principals_signer()        
        self.__email_client = EmailDPClient(config={}, signer=signer)
    
    def __get_html_email(self):
        """Retorna o HTML que inclui o link que o usuário deve utilizar 
        para redefinir sua senha."""

        email_encoded = urllib.parse.quote(f'{self.__address}')
        token_encoded = urllib.parse.quote(f'{self.__token}')       

        if ENV == 'dev':
            url_prefix = 'http://127.0.0.1:5000'
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
        html_email = self.__get_html_email()

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
