#
# app/order/api.py
#

from flask import request, jsonify
from flask_jwt_extended import jwt_required

from . import api_order_blueprint
from .order import Order
from app.pizza.pizza import Pizza


@api_order_blueprint.route('/', methods=['POST'])
@jwt_required()
def add_order():
    """Add a new Pizza Order.

    """
    data = request.get_json()
    
    try:
        pizza_id = int(data.get('id'))
    except (KeyError, ValueError,):
        return jsonify({'status': 'fail', 'message': 'null', 'data': 'null'}), 400
    
    pizza = Pizza()
    pizza_exists = pizza.exist(pizza_id)

    if not pizza_exists:
        return jsonify({'status': 'fail', 'message': 'null', 'data': 'null'}), 400
    
    #order = Order()

    # TODO: return 201