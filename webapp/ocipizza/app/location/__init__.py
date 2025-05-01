#
# /app/location/__init__.py
#

from flask import Blueprint

api_location_blueprint = Blueprint('api_location', __name__)

from . import api