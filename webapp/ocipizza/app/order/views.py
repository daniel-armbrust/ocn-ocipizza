#
# app/order/views.py
#

from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user
from flask import flash as flask_flash

from app.settings import Settings
from . import order_blueprint
from .forms import OrderAddressDeliveryForm
from .order import Order

settings = Settings()

@order_blueprint.route('/new', methods=['POST'])
@login_required
def new():
    """Add new delivery order.

    """     
    form = OrderAddressDeliveryForm() 

    pizza_list = request.form.get('pizza_list', None)
    pizza_id_list = []

    try:
        pizza_id_list = [int(item) for item in pizza_list.split(',')]
    except ValueError:
        flask_flash(u'Houve um erro ao processar o seu pedido.', 'error')        
        
        return redirect(url_for('pizza.cart_view'))
    
    if form.validate_on_submit():
        data = request.form.to_dict()

        data.pop('csrf_token')
        data.pop('next')        
        data.pop('pizza_list')

        data['id'] = int(current_user.id)
        data['pizza_id_list'] = pizza_id_list        

        order = Order()
        added = order.add(data)

        if added:
            flask_flash(u'O pedido foi adicionado com sucesso!', 'success')

            return redirect(url_for('order.list'))
    
    flask_flash(u'Houve um erro ao processar o seu pedido.', 'error')

    return redirect(url_for('pizza.cart_view'))


@order_blueprint.route('/list', methods=['GET'])
@login_required
def list():
    """List my orders.

    """
    user_id = int(current_user.id)

    order = Order()
    orders = order.list(user_id)

    return render_template('order_list.html', orders=orders,
                           web_config=settings.web_config,
                           api_config=settings.api_config)



        


