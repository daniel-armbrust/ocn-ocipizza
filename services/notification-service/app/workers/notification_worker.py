#
# worker/notification_worker.py
#

import asyncio
import logging

from app.config.settings import settings

from app.messaging.message_consumer import MessageConsumer
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

class NotificationWorker:
    """
    Executa continuamente o consumo e o processamento das mensagens
    da fila de notificações.
    """

    def __init__(self,
                 message_consumer: MessageConsumer,
                 notification_service: NotificationService):
        """
        Inicializa o worker responsável pelas notificações.

        Args:
            message_consumer: Consumidor responsável por receber e confirmar
                as mensagens da fila.
            notification_service: Serviço responsável por processar
                as notificações recebidas.
        """

        self.message_consumer = message_consumer
        self.notification_service = notification_service

    async def run(self) -> None:
        """
        Mantém o consumo das mensagens ativo durante a execução do serviço.
        """

        logger.info(
            'Consumidor da fila de notificações iniciado.'
        )

        while True:
            try:
                # Executa a operação bloqueante de leitura da fila em uma
                # thread separada para não bloquear o event loop do serviço.
                messages = await asyncio.to_thread(
                    self.message_consumer.receive
                )

                if not messages:
                    # Aguarda antes de consultar novamente quando nenhuma
                    # mensagem estiver disponível na fila.
                    await asyncio.sleep(
                        settings.notification_poll_interval
                    )
                    continue

                logger.info(
                    'Processando %s mensagem(ns) da fila de notificações.',
                    len(messages)
                )

                for message in messages:
                    await self._process_message(
                        message
                    )

            except asyncio.CancelledError:
                # Propaga o cancelamento para permitir que o worker seja
                # encerrado corretamente durante o shutdown do serviço.
                raise

            except Exception:
                # Uma falha inesperada no ciclo de consumo é registrada,
                # mas não encerra permanentemente o worker.
                logger.exception(
                    'Erro inesperado durante o consumo das notificações.'
                )

                await asyncio.sleep(
                    settings.notification_retry_interval
                )

    async def _process_message(self, message: dict) -> None:
        """
        Processa uma mensagem recebida da fila.

        Args:
            message: Mensagem contendo os dados da notificação e o
                identificador utilizado para sua confirmação.
        """
        
        receipt = message['receipt']
        body = message['body']

        try:
            # Entrega somente o conteúdo da mensagem para a camada de
            # serviço, mantendo os detalhes da fila dentro do worker.
            await asyncio.to_thread(
                self.notification_service.process,
                body
            )

            logger.info(
                'E-mail de notificação enviado com sucesso para %s.',
                body.get('recipient')
            )

            # Confirma a mensagem somente após o processamento ser
            # concluído com sucesso.
            await asyncio.to_thread(
                self.message_consumer.delete,
                receipt
            )

        except Exception:
            # A mensagem não é confirmada quando seu processamento falha.
            # Dessa forma, a infraestrutura de mensageria poderá
            # disponibilizá-la novamente conforme sua política de retry.
            logger.exception(
                'Erro ao processar uma mensagem de notificação.'
            )