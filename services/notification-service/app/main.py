#
# main.py
#

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status

from app.dependencies.worker import get_notification_worker

from app.config.settings import settings
from app.config.logging import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida do notification-service.

    Args:
        app: Instância da aplicação FastAPI.

    Yields:
        Controle para execução da aplicação.
    """
    # Obtém o worker responsável por consumir e processar
    # as mensagens da fila de notificações.
    notification_worker = get_notification_worker()

    # Inicia o worker em uma tarefa assíncrona para que o consumo
    # das mensagens aconteça durante toda a execução da aplicação.
    worker_task = asyncio.create_task(
        notification_worker.run()
    )

    logger.info('Notification worker iniciado.')

    yield

    # Solicita o encerramento da tarefa quando o serviço
    # estiver sendo finalizado.
    worker_task.cancel()

    try:
        await worker_task
    except asyncio.CancelledError:
        logger.info('Notification worker finalizado.')


app = FastAPI(
    title='OCI Pizza - Notification Service',
    version='1.0.0',
    lifespan=lifespan,
    docs_url='/docs' if settings.app_env == 'development' else None,
    redoc_url='/redoc' if settings.app_env == 'development' else None,
    openapi_url='/openapi.json' if settings.app_env == 'development' else None
)

@app.get('/health', status_code=status.HTTP_200_OK)
def health() -> dict:
    """
    Retorna o estado básico do notification-service.

    Returns:
        Informação indicando que o serviço está em execução.
    """

    return {
        'status': 'success', 
        'data': {'service': 'notification-service'}
    }

