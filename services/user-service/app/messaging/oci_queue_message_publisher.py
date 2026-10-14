#
# messaging/oci_queue_message_publisher.py
#

import json

from oci.auth.signers import InstancePrincipalsSecurityTokenSigner
from oci.queue import QueueClient
from oci.queue.models import PutMessagesDetails, PutMessagesDetailsEntry

from app.messaging.exceptions import MessagePublishError
from app.messaging.message_publisher import MessagePublisher


class OCIQueueMessagePublisher(MessagePublisher):
    """
    Implementação de MessagePublisher utilizando OCI Queue.
    """

    def __init__(self,
                 queue_id: str,
                 messages_endpoint: str,
                 region: str) -> None:
        """
        Inicializa o publicador de mensagens do OCI Queue.

        Args:
            queue_id: OCID da fila utilizada para publicação.
            messages_endpoint: Endpoint de mensagens específico da fila.
            region: Região OCI onde a fila está provisionada.
        """

        self.queue_id = queue_id
        self.messages_endpoint = messages_endpoint
        self.region = region
        self._client: QueueClient | None = None

    def publish(self, payload: dict) -> None:
        """
        Publica uma mensagem JSON no OCI Queue.

        Args:
            payload: Dados que serão serializados em JSON e publicados
                na fila.

        Returns:
            None.

        Raises:
            MessagePublishError: Caso ocorra uma falha durante a serialização,
                autenticação ou publicação da mensagem no OCI Queue.
        """

        try:
            content = json.dumps(payload)

            # Representa uma mensagem individual que será publicada na fila.
            # O conteúdo deve ser uma string, por isso o payload foi
            # previamente serializado para JSON.
            message = PutMessagesDetailsEntry(
                content=content
            )

            # Agrupa as mensagens no formato esperado pela operação
            # put_messages. A API utiliza uma lista para permitir que uma
            # única requisição publique uma ou várias mensagens.
            messages = PutMessagesDetails(
                messages=[message]
            )

            # Obtém o client autenticado por Instance Principal e envia o
            # conjunto de mensagens ao messages endpoint da fila configurada.
            self._get_client().put_messages(
                queue_id=self.queue_id,
                put_messages_details=messages
            )
        except Exception as ex:
            # A abstração de mensageria expõe uma exceção independente do
            # provider, inclusive para falhas do signer de Instance Principal.
            raise MessagePublishError(
                'Unable to publish message to OCI Queue.'
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
                service_endpoint=self.messages_endpoint,
            )

        return self._client
