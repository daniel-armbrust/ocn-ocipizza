#
# dependencies/messaging.py
#

from app.config.settings import settings
from app.messaging.message_publisher import MessagePublisher
from app.messaging.oci_queue_message_publisher import OCIQueueMessagePublisher
from app.messaging.rabbitmq_message_publisher import RabbitMQMessagePublisher


def get_message_publisher() -> MessagePublisher:
    """
    Monta o publicador de mensagens de acordo com o provider configurado.

    Returns:
        Implementação de `MessagePublisher` utilizada pela aplicação.

    Raises:
        ValueError: Caso o provider não seja suportado ou alguma configuração
            obrigatória do provider selecionado não tenha sido informada.
    """

    if settings.messaging_provider == 'rabbitmq':
        rabbitmq_settings = {
            'host': settings.rabbitmq_host,
            'port': settings.rabbitmq_port,
            'username': settings.rabbitmq_username,
            'password': settings.rabbitmq_password
        }

        missing_settings = [
            name
            for name, value in rabbitmq_settings.items()
            if value is None
        ]

        if missing_settings:
            raise ValueError(
                'Missing RabbitMQ settings: '
                f'{", ".join(missing_settings)}.'
            )

        return RabbitMQMessagePublisher(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            username=settings.rabbitmq_username,
            password=settings.rabbitmq_password,
            queue_name=settings.queue_name
        )

    if settings.messaging_provider == 'oci_queue':
        oci_queue_settings = {
            'queue_id': settings.oci_queue_id,
            'messages_endpoint': settings.oci_queue_messages_endpoint,
            'region': settings.oci_region
        }

        missing_settings = [
            name
            for name, value in oci_queue_settings.items()
            if value is None
        ]

        if missing_settings:
            raise ValueError(
                'Missing OCI Queue settings: '
                f'{", ".join(missing_settings)}.'
            )

        return OCIQueueMessagePublisher(
            queue_id=settings.oci_queue_id,
            messages_endpoint=settings.oci_queue_messages_endpoint,
            region=settings.oci_region
        )

    raise ValueError(
        f'Unsupported messaging provider: '
        f'{settings.messaging_provider}'
    )
