#
# fn-user-registry-email/modules/email.py
#

import os
import string
import secrets
from datetime import datetime
import urllib.parse
import smtplib

from oci.auth import signers as oci_signers
from oci.email_data_plane import EmailDPClient
from oci.email_data_plane.models import Sender, Recipients, SubmitEmailDetails, \
    EmailAddress

from .nosql import NoSQL

# Globals
ENV = os.environ.get('ENV')
EMAIL_COMPARTMENT_OCID = os.environ.get('EMAIL_COMPARTMENT_OCID')
TOKEN_LEN = 22
EXPIRATION_SECS = 600 # 10 minutos
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
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, value: str):
        self.__name = value

    def __init__(self):
        if ENV == 'development':
            pass
        else:
            signer = oci_signers.get_resource_principals_signer()        
            self.__email_client = EmailDPClient(config={}, signer=signer)
            
            self.__token = self.__get_token()
            self.__expiration_ts = self.__get_expiration_ts()
    
    def __get_token(self):
        """Retorna um token."""
        chars = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(chars) for _ in range(TOKEN_LEN))

        return token

    def __get_expiration_ts(self):
        """Retorna um timestamp que representa uma data de expiração futura."""
        expiration_ts = int(datetime.now().timestamp())
        expiration_ts += EXPIRATION_SECS

        return expiration_ts
    
    def __get_html_email(self):
        """Retorna o HTML que inclui o link que o usuário deve utilizar 
        para ativar a sua conta."""

        email_encoded = urllib.parse.quote(f'{self.__address}')
        token_encoded = urllib.parse.quote(f'{self.__token}')

        if ENV == 'development':
            url_prefix = f'http://{HTTP_IP}:{HTTP_PORT}'
        else:
            url_prefix = 'https://www.ocipizza.com.br'

        url = f'{url_prefix}/user/new/confirm?e={email_encoded}&t={token_encoded}'

        html_email = f'''
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head></head>
            <body>
               <h1><a href="{url}">Confirme o seu e-mail.</a></h1>
            </body>
            </html>
        '''

        return html_email

    def __add_email_verification_data(self):
        """Armazena os dados no banco NoSQL que o usuário utilizará para 
        confirmar seu cadastro por meio de um link."""
        data = {}

        data['email'] = self.__address
        data['token'] = self.__token
        data['expiration_ts'] = self.__expiration_ts

        nosql = NoSQL()

        nosql.table = 'email_verification'
        added = nosql.add(data)
        nosql.close()

        if added:
            return True
        else:
            return False
        
    def send(self):
        """Envia o e-mail para o usuário."""               
        added = self.__add_email_verification_data()
        
        if not added:
            return False
        
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

            email_to = EmailAddress(
                email=self.__address,
                name=self.__name
            )

            recipients = Recipients(to=[email_to])
                    
            email_details = SubmitEmailDetails(
                subject='OCI Pizza - Confirme o seu cadastro.',            
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