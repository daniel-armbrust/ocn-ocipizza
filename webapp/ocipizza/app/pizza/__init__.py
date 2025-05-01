#
# app/pizza/__init__.py
#

from flask import Blueprint

pizza_blueprint = Blueprint('pizza', __name__, template_folder='templates')
api_pizza_blueprint = Blueprint('api_pizza', __name__)

from . import views
from . import api