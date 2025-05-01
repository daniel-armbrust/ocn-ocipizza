#
# app/user/__init__.py
#

from flask import Blueprint

user_blueprint = Blueprint('user', __name__, template_folder='templates')
api_user_blueprint = Blueprint('api_users', __name__)

from . import views
from . import api