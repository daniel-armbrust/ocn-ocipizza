#
# app/order/__init__.py
#

from flask import Blueprint

order_blueprint = Blueprint('order', __name__, template_folder='templates')
api_order_blueprint = Blueprint('api_order', __name__)

from . import api
from . import views