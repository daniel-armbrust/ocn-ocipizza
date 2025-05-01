#
# modules/nosql.py
#

import sys

from oci import config as oci_config
from oci.auth import signers as oci_signers
from oci import nosql as oci_nosql
from oci import exceptions as oci_exceptions

from app.settings import Settings

class NoSQL():
    def __init__(self):
        self._settings = Settings()

        if self._settings.env == 'dev':
            config = oci_config.from_file(file_location=self._settings.oci_config_file)   
            oci_config.validate_config(config)
            
            self._nosql = oci_nosql.NosqlClient(config=config)
        else:
            signer = oci_signers.get_resource_principals_signer()
            self._nosql = oci_nosql.NosqlClient(config={}, signer=signer)
    
    def query(self, sql: str):
        query_details = oci_nosql.models.QueryDetails(
            consistency='EVENTUAL',
            statement=sql,
            compartment_id=self._settings.nosql_compartment_ocid           
        )
        
        # TODO: check READ exception
        try:
            resp = self._nosql.query(query_details=query_details)
        except (oci_exceptions.ServiceError, oci_exceptions.ConnectTimeout,) as e:
            sys.stderr.write(f'{e}')
            return None

        return resp.data.items
    
    def save(self, table_name: str, data: dict):
        # This will update a value or insert a new value.
        # IF_ABSENT = insert
        # IF_PRESENT = update 
        update_row_details = oci_nosql.models.UpdateRowDetails(
            compartment_id=self._settings.nosql_compartment_ocid,
            value=data,
            option='IF_ABSENT'
        )    

        try:
            resp = self._nosql.update_row(table_name_or_id=table_name,
                                          update_row_details=update_row_details)
        except (oci_exceptions.ServiceError, oci_exceptions.ConnectTimeout,) as e:            
            sys.stderr.write(f'{e}')
            return False        
        
        # TODO: register log in case of failure.

        if resp.status == 200:
            return True
        else:
            return False