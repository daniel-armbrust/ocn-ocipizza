#
# nosql/nosql-init/init.py
#

import os
import sys
import json
import time

from borneo import AuthorizationProvider, NoSQLHandle, \
                   NoSQLHandleConfig, PutRequest, PutOption, \
                   TableLimits, TableRequest

# Lista de arquivos DDL que devem ser processados em ordem.
ORDERED_DLL_FILES_LIST = ('user.ddl', 'user-order.ddl', 'pizza.ddl',)

# Nome da Table e Arquivo JSON contendo os dados para inserção.
TABLE_DATA = {'pizza': 'pizza.json'}

# IP e Porta para conexão com o Oracle Cloud NoSQL Simulator.
NOSQL_CLOUDSIM_IP = os.getenv('NOSQL_CLOUDSIM_IP')
NOSQL_CLOUDSIM_PORT = os.getenv('NOSQL_CLOUDSIM_PORT')

# Prefixo URL utilizado para salvar as imagens.
BUCKET_URL_PREFIX = os.getenv('BUCKET_URL_PREFIX')

class CloudsimAuthorizationProvider(AuthorizationProvider):
    """
    Cloud Simulator Only.

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


def exec_ddl_statement():
    """Executa os arquivos DDL.
    
    """        
    for ddl_file in ORDERED_DLL_FILES_LIST:
        ddl_filepath = f'ddl/{ddl_file}'

        print(f'[INFO] Creating table from DDL: {ddl_filepath} ...', end='')
      
        with open(ddl_filepath, 'r') as f:
            ddl_statement = f.read()

            table_request = TableRequest()

            # Cannot set limits on child table: user.order
            if 'user-order' not in ddl_file:
                table_limits = TableLimits(5, 5, 1)
                table_request.set_table_limits(table_limits)

            table_request.set_statement(ddl_statement)    

            for i in range(3):
                try:
                    nosql_handle.table_request(table_request)
                except:
                    time.sleep(3)
                else:
                    break

        print(' Done.')
        

def insert_data():
    """Inserção dos dados a partir dos arquivos JSON.

    """    
    for table_name, json_file in TABLE_DATA.items():
        json_filepath = f'data/{json_file}'

        print(f'[INFO] Insert data from file: {json_filepath} ...', end='')

        with open(json_filepath, 'r') as f:
            put_request = PutRequest()
            put_request.set_table_name(table_name)
            put_request.set_option(PutOption.IF_ABSENT)

            for line in f:
                json_line = json.loads(line)
                image_file = json_line['image']

                # Atualiza para a URL da imagem.
                json_line['image'] = f'{BUCKET_URL_PREFIX}/{image_file}'

                put_request.set_value(json_line)
                
                for i in range(3):
                    try:
                        nosql_handle.put(put_request)
                    except:
                        time.sleep(3)
                    else:
                        break                
        
        print(f' Done.')


cloudsim_endpoint = f'{NOSQL_CLOUDSIM_IP}:{NOSQL_CLOUDSIM_PORT}'
kvstore_endpoint = f'{NOSQL_CLOUDSIM_IP}:80'
cloudsim_id = 'cloudsim'

endpoint = cloudsim_endpoint
provider = CloudsimAuthorizationProvider(cloudsim_id)

nosql_handle = NoSQLHandle(NoSQLHandleConfig(endpoint, provider))

exec_ddl_statement()
insert_data()

nosql_handle.close()

sys.exit(0)