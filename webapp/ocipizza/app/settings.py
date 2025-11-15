#
# app/settings.py
#

import os
from datetime import datetime, timedelta

import oci

class Settings():
    def __init__(self):
        self.env = os.environ.get('FLASK_ENV') or 'development'

        if self.env == 'development':
            import secrets

            self.secret_key = secrets.token_hex(32)

            self.web_config = {'scheme': 'http', 'host': '127.0.0.1', 'port': '5000'}
            self.api_config = {'scheme': 'http', 'host': '127.0.0.1', 'port': '5000'}            
                        
            self.domain = None
            self.cookie_secure = False
            self.html_minify = False 

            # Região do OCI obtida a partir do arquivo de configuração ~/.oci/config.
            oci_config = oci.config.from_file(file_location='~/.oci/config')     
            self.oci_region = oci_config.get('region')
        else:
            self.secret_key = os.environ.get('SECRET_KEY')
            
            self.web_config = {'scheme': 'https', 'host': 'www.ocipizza.dev.br', 'port': '443'}
            self.api_config = {'scheme': 'https', 'host': 'api.ocipizza.dev.br', 'port': '443'}         

            self.html_minify = True

            self.domain = self.web_config['host']
            self.cookie_secure = True       

            # Região do OCI onde a aplicação está sendo executada.
            signer = oci.auth.signers.get_resource_principals_signer()           
            self.oci_region = signer.region              

        # OCI Object Storage Namespace.
        self.oci_objs_namespace = os.environ.get('OCI_OBJS_NAMESPACE')

        # OCID das funções no OCI.
        self.fn_user_register_ocid = os.environ.get('FN_USER_REGISTER_OCID')
        self.fn_password_recovery_ocid = os.environ.get('FN_PASSWORD_RECOVERY_OCID')

        # OCID do compartimento do NoSQL.
        self.nosql_compartment_ocid = os.environ.get('NOSQL_COMPARTMENT_OCID')
                
        self.user_min_password_length = 8    
        self.user_max_password_length = 16

        datetime_now = datetime.now()
        expire_timedelta = datetime_now + timedelta(hours=2)
        expire_ts = int(expire_timedelta.strftime('%s'))

        # JWT
        self.jwt_cookie_name = 'ocipzjwt'
        #self.jwt_cookie_expire_ts = expire_ts

        # Flask Session
        self.session_cookie_name = 'ocipzsess'
        self.session_cookie_expire_ts = expire_ts