#
# app/pizza/api.py
#

from flask import jsonify

from . import api_pizza_blueprint
from .pizza import Pizza

# /pizzas
@api_pizza_blueprint.route('', methods=['GET'])
def list_pizzas():
    """Return ALL pizzas.
    
    """
    pizza = Pizza()
    data = pizza.list()

    if not data:
        return jsonify({'status': 'fail', 'message': 'null', 'data': 'null'}), 404
    else:
        return jsonify({'status': 'success', 'message': 'null', 'data': data})


@api_pizza_blueprint.route('/<int:id>', methods=['GET'])
def read_pizza(id: int):
    """Return a pizza by id.

    """
    pizza = Pizza()
    data = pizza.get(id)

    if not data:
        return jsonify({'status': 'fail', 'message': 'Not found.', 'data': 'null'}), 404
    else:
        return jsonify({'status': 'success', 'message': 'null', 'data': data})