#
# notifications/email_templates.py
#

EMAIL_TEMPLATES = {
    'USER_CONFIRMATION': {
        'subject': 'Confirme seu e-mail',
        'html': 'user_confirmation.html'
    },
    'ORDER_SENT': {
        'subject': 'Seu pedido saiu para entrega',
        'html': 'order_sent.html'
    }
}