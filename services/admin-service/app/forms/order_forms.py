#
# forms/order_forms.py
#

from wtforms import Form, SelectField
from wtforms.validators import DataRequired


class OrderStatusForm(Form):
    """
    Define e valida o status submetido pelos painéis de pedidos.
    """

    status = SelectField(
        'Status',
        choices=[
            ('RECEIVED', 'Recebido'),
            ('PREPARING', 'Em preparo'),
            ('READY', 'Pronto'),
            ('OUT_FOR_DELIVERY', 'Em entrega'),
            ('DELIVERED', 'Entregue'),
            ('CANCELLED', 'Cancelado')
        ],
        validators=[
            DataRequired(message='Selecione um status.')
        ],
        render_kw={
            'required': True
        }
    )


class OrderDeleteForm(Form):
    """
    Representa o formulário de confirmação da exclusão de um pedido.
    """

    pass
