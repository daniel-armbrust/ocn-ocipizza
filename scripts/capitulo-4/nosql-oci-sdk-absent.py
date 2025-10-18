#!/usr/bin/env python3

import oci

COMPARTMENT_ID = ''

new_user_data = {
    'id': 3, 
    'name': 'Giovanna Armbrust', 
    'email': 'gi.armbrust@ocipizza.com.br',
    'telephone': '88777777777'
}

config = oci.config.from_file(file_location='~/.oci/config')
nosql_client = oci.nosql.NosqlClient(config=config)

update_row_details = oci.nosql.models.UpdateRowDetails(
    compartment_id=COMPARTMENT_ID,
    option='IF_ABSENT',
    value=new_user_data
)

nosql_client.update_row(
    table_name_or_id='user',
    update_row_details=update_row_details
)