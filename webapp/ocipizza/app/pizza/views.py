#
# app/pizza/views.py
#

from flask import render_template

from app.settings import Settings
from . import pizza_blueprint
from app.order.forms import OrderAddressDeliveryForm

settings = Settings()

@pizza_blueprint.route('/cart', methods=['GET'])
def cart_view():
    """Displays the pizza cart page.

    """
    form = OrderAddressDeliveryForm()

    return render_template('pizza_cart.html', form=form,
                           web_config=settings.web_config,
                           api_config=settings.api_config)
