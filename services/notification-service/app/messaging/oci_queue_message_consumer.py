#
# messaging/oci_queue_message_consumer.py
#

import json

from oci.auth.signers import InstancePrincipalsSecurityTokenSigner
from oci.queue import QueueClient

from app.messaging.exceptions import MessageConsumeError
from app.messaging.message_consumer import MessageConsumer


class OCIQueueMessageConsumer(MessageConsumer):
    """Implementação de MessageConsumer utilizando OCI Queue."""

    def __init__(self,
                 queue_id: str,
                 messages_endpoint: str,
                 region: str) -> None:
        """
        Inicializa o consumidor de mensagens do OCI Queue.

        Args:
            queue_id: OCID da fila utilizada para consumo.
            messages_endpoint: Endpoint de mensagens específico da fila.
            region: Região OCI onde a fila está provisionada.
        """

        self.queue_id = queue_id
        self.messages_endpoint = messages_endpoint
        self.region = region
        self._client: QueueClient | None = None

    def receive(self) -> list[dict]:
        """
        Recebe uma mensagem disponível no OCI Queue.

        Returns:
            Lista contendo a mensagem recebida ou uma lista vazia quando
            nenhuma mensagem estiver disponível.

        Raises:
            MessageConsumeError: Caso ocorra uma falha durante a autenticação,
                leitura ou desserialização da mensagem.
        """

        try:
            # Solicita no máximo uma mensagem. O serviço aplica o tempo de
            # visibilidade e o long polling configurados na própria fila.
            response = self._get_client().get_messages(
                queue_id=self.queue_id,
                limit=1
            )

            received_messages = response.data.messages

            if not received_messages:
                return []

            # GetMessage contém o conteúdo publicado e um receipt opaco que
            # identifica a entrega para exclusão após o processamento.
            message = received_messages[0]

            try:
                message_body = json.loads(message.content)
            except (TypeError, json.JSONDecodeError):
                # Remove mensagens inválidas para evitar novas entregas de um
                # conteúdo que não poderá ser processado como JSON.
                self._get_client().delete_message(
                    queue_id=self.queue_id,
                    message_receipt=message.receipt
                )
                raise

            return [{
                'receipt': message.receipt,
                'body': message_body
            }]
        except Exception as ex:
            # A abstração expõe uma exceção independente do provider, inclusive
            # para falhas do signer de Instance Principal.
            raise MessageConsumeError(
                'Unable to consume message from OCI Queue.'
            ) from ex

    def delete(self, receipt: str) -> None:
        """
        Remove do OCI Queue uma mensagem processada com sucesso.

        Args:
            receipt: Token opaco retornado pelo OCI Queue para a entrega.

        Raises:
            MessageConsumeError: Caso a mensagem não possa ser removida.
        """

        try:
            # O receipt identifica a entrega que deve ser excluída. Depois
            # desta chamada, a mensagem não volta a ficar visível na fila.
            self._get_client().delete_message(
                queue_id=self.queue_id,
                message_receipt=receipt
            )
        except Exception as ex:
            raise MessageConsumeError(
                'Unable to delete message from OCI Queue.'
            ) from ex

    def _get_client(self) -> QueueClient:
        """
        Cria o client OCI Queue autenticado por Instance Principal.

        Returns:
            Client configurado com o endpoint de mensagens da fila.
        """

        if self._client is None:
            signer = InstancePrincipalsSecurityTokenSigner()
            
            self._client = QueueClient(
                config={'region': self.region},
                signer=signer,
                service_endpoint=self.messages_endpoint
            )

        return self._client
