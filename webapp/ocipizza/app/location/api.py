#
# app/location/api.py
#

from flask import jsonify

from . import api_location_blueprint
from .location import Zipcode

@api_location_blueprint.route('/zipcodes/<zipcode>', methods=['GET'])
def get_state_city(zipcode: str):
    """Return state and city from zipcode.

    """
    location = Zipcode()   
    (state, city,) = location.get_state_city(zipcode)
        
    if state and city:
        return jsonify({'status': 'success', 'message': 'null', 
                        'data': {'state': state, 'city': city}}), 200
    else:
        return jsonify({'status': 'fail', 
                        'message': 'Cannot find state and city from zipcode.', 
                        'data': 'null'}), 404