#
# modules/nosql.py
#

import logging

from flask import current_app as app
from app.settings import Settings

from borneo.iam import SignatureProvider
from borneo import NoSQLHandleConfig, NoSQLHandle
from borneo import Consistency, QueryRequest
from borneo import PutRequest, PutOption
from borneo.kv import StoreAccessTokenProvider

class NoSQL():
    _nosql_handle = None
    
    @staticmethod
    def create_handler(env: str):
        settings = Settings() 
       
        nosql_handle_config = NoSQLHandleConfig(settings.oci_region)
        sigprov = None

        if env == 'development':         
            log_stdout = logging.basicConfig(level=logging.INFO, 
                                             format='%(asctime)s - %(levelname)s - %(message)s',
                                             handlers=[logging.StreamHandler()])
            
            sigprov = SignatureProvider(config_file='~/.oci/config')
            nosql_handle_config.set_logger(log_stdout)

        else:
            sigprov = SignatureProvider.create_with_resource_principal()  
            nosql_handle_config.set_logger(None)

        nosql_handle_config.set_authorization_provider(sigprov)
        nosql_handle_config.set_default_compartment(settings.nosql_compartment_ocid)
                
        nosql_handle = NoSQLHandle(nosql_handle_config) 

        return nosql_handle

    def __init__(self):
         self._nosql_handle = app._nosql_handle 
    
    def query(self, sql: str):
        result = []

        query_request = QueryRequest()
        query_request.set_consistency(Consistency.EVENTUAL)        
        nosql_request = query_request.set_statement(sql)

        query_request.close()
        
        while True:
            query = self._nosql_handle.query(query_request)
            result = query.get_results()
      
            if len(result) > 0:          
                break        

            if nosql_request.is_done():
                break
            
        return result        
    
    def save(self, table_name: str, data: dict):
        put_request = PutRequest()
        
        put_request.set_table_name(table_name)
        put_request.set_option(PutOption.IF_ABSENT)
        put_request.set_value(data)

        result = self._nosql_handle.put(put_request)

        # A successful put returns a non-empty version.
        if result.get_version() is not None:
            generated_value = result.get_generated_value()

            if generated_value:
                return generated_value              
            else:
                return True
        else:
            return False