#
# app/user/__init__.py
#

from flask import Blueprint, jsonify

user_blueprint = Blueprint('user', __name__, template_folder='templates')
api_user_blueprint = Blueprint('api_users', __name__)

from . import views
from . import api

@api_user_blueprint.app_errorhandler(404)
def not_found():
    return jsonify({'status': 'fail', 'message': 'Resource not found.', 
                    'data': 'null'}), 404