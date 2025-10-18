#!/usr/bin/env python3

from borneo.iam import SignatureProvider
from borneo import NoSQLHandleConfig, NoSQLHandle, Regions
from borneo import PutRequest, PutOption

COMPARTMENT_ID = ''

new_user_data = {
    'id': 3,
    'name': 'Giovanna Armbrust',
    'email': 'gi.armbrust@ocipizza.com.br',
    'telephone': '88777777777'
}

sigprov = SignatureProvider(config_file='~/.oci/config')

nosql_handle_config = NoSQLHandleConfig(Regions.SA_SAOPAULO_1)
nosql_handle_config.set_authorization_provider(sigprov)
nosql_handle_config.set_default_compartment(COMPARTMENT_ID)

nosql_handle = NoSQLHandle(nosql_handle_config)

put_request = PutRequest()
put_request.set_option(PutOption.IF_ABSENT)
put_request.set_table_name('user')
put_request.set_value(new_user_data)
put_request.set_return_row(True)

nosql_handle.put(put_request)

nosql_handle.close()