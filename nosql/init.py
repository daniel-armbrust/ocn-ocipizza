#
# nosql/nosql-init/init.py
#

import os
import sys
import json
import time
import logging

from borneo import NoSQLHandle, NoSQLHandleConfig, PutRequest, \
                   PutOption, TableLimits, TableRequest
from borneo.kv import StoreAccessTokenProvider

# Lista de arquivos DDL que devem ser processados em ordem.
ORDERED_DLL_FILES_LIST = (
    'user.ddl', 
    'user-order.ddl', 
    'pizza.ddl', 
    'email-verification.ddl'
)

# Nome da Table e Arquivo JSON contendo os dados para inserção.
TABLE_DATA = {'pizza': 'pizza.json'}

# IP e Porta para conexão com o Oracle Cloud NoSQL Simulator.
NOSQL_IP = os.getenv('NOSQL_IP')
NOSQL_PORT = os.getenv('NOSQL_PORT')

# Prefixo URL utilizado para salvar as imagens.
BUCKET_URL_PREFIX = os.getenv('BUCKET_URL_PREFIX')

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


log_stdout = logging.basicConfig(level=logging.INFO,
                                 format='%(asctime)s - %(levelname)s - %(message)s',
                                 handlers=[logging.StreamHandler()])

provider = StoreAccessTokenProvider()
config = NoSQLHandleConfig(f'http://{NOSQL_IP}:{NOSQL_PORT}', provider).set_logger(log_stdout)
nosql_handle = NoSQLHandle(config)

exec_ddl_statement()
insert_data()

nosql_handle.close()

sys.exit(0)