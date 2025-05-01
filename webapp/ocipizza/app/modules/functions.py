#
# modules/functions.py
#
import sys
import json
import threading

from oci import config as oci_config
from oci.auth import signers as oci_signers
from oci import exceptions as oci_exceptions
from oci import functions

from app.settings import Settings

class Functions():
    @property
    def fn_ocid(self):
        return self.__fn_ocid
    
    @fn_ocid.setter
    def fn_ocid(self, value: str):
        self.__fn_ocid = value
        
    def __init__(self):
        self.__settings = Settings()

    def __get_fn_endpoint(self):
        fn_mgm_client = None

        if self.__settings.env == 'dev':
            config = oci_config.from_file(file_location=self.__settings.oci_config_file)   
            oci_config.validate_config(config)

            fn_mgm_client = functions.FunctionsManagementClient(config=config)
        else:
            signer = oci_signers.get_resource_principals_signer()
            fn_mgm_client = functions.FunctionsManagementClient(config={}, signer=signer)
        
        try:
            fn_summary = fn_mgm_client.get_function(function_id=self.__fn_ocid).data
        except (oci_exceptions.ServiceError, oci_exceptions.ConnectTimeout,) as e:
            sys.stderr.write(f'{e}')
        
        if fn_mgm_client is not None:
            return fn_summary.invoke_endpoint
        else:
            return None
        
    def __call_fn(self, json_message: str):         
        fn_client = None      
        fn_endpoint = self.__get_fn_endpoint()

        if fn_endpoint is None:
            return False
         
        if self.__settings.env == 'dev':            
           config = oci_config.from_file(file_location=self.__settings.oci_config_file)   
           oci_config.validate_config(config)        

           fn_client = functions.FunctionsInvokeClient(config=config, service_endpoint=fn_endpoint)                        
        else:
           signer = oci_signers.get_resource_principals_signer()            
           fn_client = functions.FunctionsInvokeClient(config={}, signer=signer, service_endpoint=fn_endpoint)

        try:
            fn_client.invoke_function(
                function_id=self.__fn_ocid,
                invoke_function_body=json_message,
                fn_intent='httprequest',
                fn_invoke_type='detached',
            )
        except (oci_exceptions.ServiceError, oci_exceptions.ConnectTimeout,) as e:
            sys.stderr.write(f'{e}')
        
    def invoke(self, json_message: dict):
        json_message = json.dumps(json_message)

        thread = threading.Thread(target=self.__call_fn, args=(json_message,))
        thread.daemon = True

        try:
            thread.start()
        except (SystemError, MemoryError,) as e:
            sys.stderr.write(f'{e}')

        return True