#
# dependencies/messaging.py
#

from app.config.settings import settings

from app.messaging.message_publisher import MessagePublisher
from app.messaging.rabbitmq_message_publisher import RabbitMqMessagePublisher
from app.messaging.oci_queue_message_publisher import OciQueueMessagePublisher


def get_message_publisher() -> MessagePublisher:
    """
    Monta o publicador de mensagens de acordo com o provider configurado.

    Returns:
        Implementação de `MessagePublisher` utilizada pela aplicação.

    Raises:
        ValueError: Caso o provider de mensageria configurado não seja suportado.
    """

    if settings.messaging_provider == 'rabbitmq':
        return RabbitMqMessagePublisher()

    if settings.messaging_provider == 'oci_queue':
        return OciQueueMessagePublisher()

    raise ValueError(
        f'Unsupported messaging provider: ' 
        f'{settings.messaging_provider}'
    )