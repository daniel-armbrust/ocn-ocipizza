#
# app/pizza/__init__.py
#

from flask import Blueprint, jsonify

pizza_blueprint = Blueprint('pizza', __name__, template_folder='templates')
api_pizza_blueprint = Blueprint('api_pizza', __name__)

from . import views
from . import api

@api_pizza_blueprint.app_errorhandler(404)
def not_found(error):
    return jsonify({'status': 'fail', 'message': 'Resource not found.', 
                    'data': 'null'}), 404