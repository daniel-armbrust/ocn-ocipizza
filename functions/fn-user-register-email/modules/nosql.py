#
# fn-user-registry-email/modules/nosql.py
#

import os
import logging

from borneo import AuthorizationProvider, NoSQLHandle, NoSQLHandleConfig, \
    QueryRequest, PutRequest, PutOption
from borneo.iam import SignatureProvider

# Globals
ENV = os.environ.get('ENV')
NOSQL_COMPARTMENT_OCID = os.environ.get('NOSQL_COMPARTMENT_OCID')
OCI_REGION = os.environ.get('OCI_REGION')
NOSQL_CLOUDSIM_IP = os.getenv('NOSQL_CLOUDSIM_IP')
NOSQL_CLOUDSIM_PORT = os.getenv('NOSQL_CLOUDSIM_PORT') 

class CloudsimAuthorizationProvider(AuthorizationProvider):
    """
    NoSQL Cloud Simulator Only.

    This class is used as an AuthorizationProvider when using the Cloud
    Simulator, which has no security configuration. It accepts a string
    tenant_id that is used as a simple namespace for tables.
    """
    def __init__(self, tenant_id):
        super(CloudsimAuthorizationProvider, self).__init__()
        self._tenant_id = tenant_id

    def close(self):
        pass

    def get_authorization_string(self, request=None):
        return 'Bearer ' + self._tenant_id

class NoSQL():
    @property
    def table(self):
        """Getter para o nome da tabela."""
        return self.__table
    
    @table.setter
    def table(self, value: str):
        self.__table = value

    def __init__(self):
        if ENV == 'development':
            log_stdout = logging.basicConfig(level=logging.INFO, 
                                             format='%(asctime)s - %(levelname)s - %(message)s',
                                             handlers=[logging.StreamHandler()])
            
            cloudsim_endpoint = f'{NOSQL_CLOUDSIM_IP}:{NOSQL_CLOUDSIM_PORT}'
            cloudsim_id = 'cloudsim'

            endpoint = cloudsim_endpoint
            provider = CloudsimAuthorizationProvider(cloudsim_id) 

            nosql_handle_config = NoSQLHandleConfig(endpoint, provider)
            nosql_handle_config.set_logger(log_stdout)

            self.__nosql = NoSQLHandle(nosql_handle_config)            
        else:
            provider = SignatureProvider.create_with_resource_principal()        
            nosql_handle_config = NoSQLHandleConfig(OCI_REGION, provider).set_logger(None).set_default_compartment(NOSQL_COMPARTMENT_OCID)
            
            self.__nosql = NoSQLHandle(nosql_handle_config)
        
    def query(self, sql: str):
        query_request = QueryRequest().set_statement(sql)
        query_request.close()

        query_result = self.__nosql.query(query_request)

        return query_result.get_results()

    def add(self, data: dict):        
        put_request = PutRequest()
        put_request.set_table_name(self.__table)
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