#!/usr/bin/env python3

from borneo.iam import SignatureProvider
from borneo import NoSQLHandleConfig, NoSQLHandle, Regions
from borneo import Consistency, QueryRequest

COMPARTMENT_ID = ''

sigprov = SignatureProvider(config_file='~/.oci/config')

nosql_handle_config = NoSQLHandleConfig(Regions.SA_SAOPAULO_1)
nosql_handle_config.set_authorization_provider(sigprov)
nosql_handle_config.set_default_compartment(COMPARTMENT_ID)

nosql_handle = NoSQLHandle(nosql_handle_config)

query_request = QueryRequest()
query_request.set_consistency(Consistency.ABSOLUTE)        
query_request.set_statement('SELECT max(id) FROM user')

resp = nosql_handle.query(query_request)

nosql_handle.close()

print(resp.get_results())
