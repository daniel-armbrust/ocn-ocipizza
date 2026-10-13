#
# dependencies/worker.py
#

from app.dependencies.messaging import get_message_consumer
from app.services.notification_service import get_notification_service

from app.workers.notification_worker import NotificationWorker


def get_notification_worker() -> NotificationWorker:
    """
    Obtém o worker responsável pelo consumo e processamento das notificações.

    Returns:
        Worker configurado para consumir e processar as mensagens
        da fila de notificações.
    """
    return NotificationWorker(
        message_consumer=get_message_consumer(),
        notification_service=get_notification_service()
    )