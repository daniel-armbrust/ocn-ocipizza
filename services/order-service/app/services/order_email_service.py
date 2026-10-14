#
# services/order_email_service.py
#

from fastapi import Depends

from app.messaging.message_publisher import MessagePublisher
from app.dependencies.messaging import get_message_publisher

from app.messaging.exceptions import MessagePublishError
from app.exceptions.order_exceptions import OrderEmailPublishError

from app.models.order import Order


class OrderEmailService:
    """
    Implementa a publicação das notificações por e-mail relacionadas
    aos pedidos.
    """
    
    def __init__(self, message_publisher: MessagePublisher):
        """
        Inicializa o serviço responsável pelas notificações dos pedidos.

        Args:
            message_publisher: Publicador utilizado para enviar mensagens
                para a fila de notificações.
        """

        self.message_publisher = message_publisher

    def send_order_received(self, order: Order) -> None:
        """
        Publica uma mensagem para envio do e-mail de pedido recebido.

        Args:
            order: Pedido confirmado e com pagamento processado com sucesso.
        """

        # Monta o payload com os dados necessários para que o
        # notification-service gere o e-mail de pedido recebido.
        payload = {
            'type': 'ORDER_RECEIVED',
            'recipient': order.customer.email,
            'full_name': order.customer.name,
            'order_id': str(order.id),
            'items': [
                {
                    'name': item.name,
                    'quantity': item.quantity,
                    'unit_price': format(item.unit_price, '.2f'),
                    'total': format(item.subtotal, '.2f')
                }
                for item in order.items
            ],
            'subtotal': format(order.subtotal, '.2f'),
            'delivery_fee': format(order.delivery_fee, '.2f'),
            'total': format(order.total, '.2f')
        }

        try:
            # Publica a mensagem na fila para que o notification-service
            # realize o envio do e-mail através do provedor SMTP.
            self.message_publisher.publish(payload)
        except MessagePublishError as ex: 
            raise OrderEmailPublishError( 
                'Unable to publish order received email notification.' 
            ) from ex


def get_order_email_service(
        message_publisher: MessagePublisher = Depends(
            get_message_publisher
        )
) -> OrderEmailService:
    """
    Obtém o serviço responsável pela publicação das notificações
    por e-mail relacionadas aos pedidos.

    Args:
        message_publisher: Publicador responsável por enviar mensagens
            para a fila de notificações.

    Returns:
        Serviço responsável pela publicação das notificações
        por e-mail dos pedidos.
    """

    return OrderEmailService(
        message_publisher=message_publisher
    )
