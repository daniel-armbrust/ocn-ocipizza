#
# fn-password-recovery-email/modules/nosql.py
#

import os

from borneo import NoSQLHandle, NoSQLHandleConfig, QueryRequest, \
    PutRequest, PutOption
from borneo.iam import SignatureProvider

# Globals
NOSQL_COMPARTMENT_OCID = os.environ.get('NOSQL_COMPARTMENT_OCID')
OCI_REGION = os.environ.get('OCI_REGION')

class NoSQL():
    def __init__(self):
        provider = SignatureProvider.create_with_resource_principal()        
        nosql_handle_config = NoSQLHandleConfig(os.getenv('NOSQL_REGION'), provider).set_logger(None).set_default_compartment(NOSQL_COMPARTMENT_OCID)
        
        self.__nosql = NoSQLHandle(nosql_handle_config)
    
    def query(self, sql: str):
        query_request = QueryRequest().set_statement(sql)
        query_request.close()

        query_result = self.__nosql.query(query_request)

        return query_result.get_results()
    
    def add(self, data: dict):        
        put_request = PutRequest()
        put_request.set_table_name('email_verification')
        put_request.set_option(PutOption.IF_ABSENT)
        put_request.set_value(data)

        result = self.__nosql.put(put_request)

        # A successful put returns a non-empty version.
        if result.get_version() is not None:
            return True
        else:
            return False
    
    def close(self):
        self.__nosql.close()
