#
# /app/location/__init__.py
#

from flask import Blueprint, jsonify

api_location_blueprint = Blueprint('api_location', __name__)

from . import api

@api_location_blueprint.app_errorhandler(404)
def not_found(error):
    return jsonify({'status': 'fail', 'message': 'Resource not found.', 
                    'data': 'null'}), 404