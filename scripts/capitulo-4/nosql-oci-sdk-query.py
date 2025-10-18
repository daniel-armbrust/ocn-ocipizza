#!/usr/bin/env python3

import oci

COMPARTMENT_ID = ''

config = oci.config.from_file(file_location='~/.oci/config')
nosql_client = oci.nosql.NosqlClient(config=config)

query_details = oci.nosql.models.QueryDetails(
    compartment_id=COMPARTMENT_ID,
    consistency='ABSOLUTE',
    statement='SELECT name, telephone FROM user WHERE id=1'
)

resp = nosql_client.query(query_details=query_details)

print(resp.data)