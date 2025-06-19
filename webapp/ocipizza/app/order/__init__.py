#
# app/order/__init__.py
#

from flask import Blueprint, jsonify

order_blueprint = Blueprint('order', __name__, template_folder='templates')
api_order_blueprint = Blueprint('api_order', __name__)

from . import api
from . import views

@api_order_blueprint.app_errorhandler(404)
def not_found(error):
    return jsonify({'status': 'fail', 'message': 'Resource not found.', 
                    'data': 'null'}), 404