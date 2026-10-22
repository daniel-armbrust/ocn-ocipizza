#
# messaging/oci_queue_message_publisher.py
#

import json

import oci
from oci.auth.signers import InstancePrincipalsSecurityTokenSigner
from oci.queue import QueueClient
from oci.queue.models import PutMessagesDetails, PutMessagesDetailsEntry

from app.config.settings import settings
from app.messaging.exceptions import MessagePublishError
from app.messaging.message_publisher import MessagePublisher


class OCIQueueMessagePublisher(MessagePublisher):
    """
    Implementação de MessagePublisher utilizando OCI Queue.
    """

    def __init__(self, queue_id: str) -> None:
        """
        Inicializa o publicador de mensagens do OCI Queue.

        Args:
            queue_id: OCID da fila utilizada para publicação.
            messages_endpoint: Endpoint de mensagens específico da fila.
            region: Região OCI onde a fila está provisionada.
        """

        self.queue_id = queue_id
        self._client = None

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
        Cria o cliente OCI Queue utilizando a estratégia de autenticação 
        configurada.

        A região é identificada a partir do profile OCI ou automaticamente
        pela Compute Instance. O endpoint de mensagens é obtido por meio
        dos metadados da fila.

        Returns:
            Cliente OCI Queue configurado para publicação e consumo de 
                mensagens.
        """

        if self._client is None:
            # Utiliza o arquivo de configuração OCI para autenticação,
            # normalmente durante a execução local da aplicação.
            if settings.oci_auth_mode == 'config_file':

                config = oci.config.from_file(
                    file_location=settings.oci_config_file,
                    profile_name=settings.oci_config_profile
                )
                
                # Obtém a região a partir do arquivo de configuração.
                self.region = settings.oci_region
                config['region'] = settings.oci_region

                # Consulta os metadados da fila para obter seu endpoint 
                # de mensagens.
                admin_client = oci.queue.QueueAdminClient(config=config)
                queue = admin_client.get_queue(queue_id=self.queue_id).data

                self._client = QueueClient(
                    config=config,
                    service_endpoint=queue.messages_endpoint
                )

            elif settings.oci_auth_mode == 'instance_principal':
                signer = InstancePrincipalsSecurityTokenSigner()

                # Obtém a região automaticamente com base na localidade 
                # em que a aplicação está sendo executada no OCI.
                self.region = signer.region

                config = {
                    'region': self.region
                }

                # Consulta os metadados da fila para obter seu endpoint 
                # de mensagens.
                admin_client = oci.queue.QueueAdminClient(
                    config=config,
                    signer=signer
                )

                queue = admin_client.get_queue(queue_id=self.queue_id).data

                # Inicializa o cliente utilizando o endpoint da fila.
                self._client = QueueClient(
                    config=config,
                    signer=signer,
                    service_endpoint=queue.messages_endpoint
                )

        return self._client