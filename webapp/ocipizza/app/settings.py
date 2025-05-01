#
# app/settings.py
#

import os
from datetime import datetime, timedelta

class Settings():
    def __init__(self):
        self.env = os.environ.get('ENV') or 'dev'          

        if self.env == 'dev':
            import secrets

            self.secret_key = secrets.token_hex(32)

            self.web_config = {'scheme': 'http', 'host': '127.0.0.1', 'port': '5000'}
            self.api_config = {'scheme': 'http', 'host': '127.0.0.1', 'port': '5000'}            
                        
            self.domain = None
            self.cookie_secure = False
            self.html_minify = False                    
        else:
            self.secret_key = os.environ.get('SECRET_KEY')
            
            self.web_config = {'scheme': 'https', 'host': 'www.ocipizza.dev.br', 'port': '443'}
            self.api_config = {'scheme': 'https', 'host': 'api.ocipizza.dev.br', 'port': '443'}         

            self.html_minify = True

            self.domain = self.web_config['host']
            self.cookie_secure = True                    
            
        self.oci_config_file = os.environ.get('OCI_CONFIG_FILE') or '~/.oci/config'
        self.nosql_compartment_ocid = os.environ.get('NOSQL_COMPARTMENT_OCID')   
        self.fn_user_register_ocid = os.environ.get('FN_USER_REGISTER_OCID')
        self.fn_password_recovery_ocid = os.environ.get('FN_PASSWORD_RECOVERY_OCID')

        self.user_min_password_length = 8    
        self.user_max_password_length = 16

        datetime_now = datetime.now()
        expire_timedelta = datetime_now + timedelta(hours=2)
        expire_ts = int(expire_timedelta.strftime('%s'))

        self.jwt_cookie_name = 'ocipzjwt'
        self.jwt_cookie_expire_ts = expire_ts

        self.session_cookie_name = 'ocipzsess'
        self.session_cookie_expire_ts = expire_ts