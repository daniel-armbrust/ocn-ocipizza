#
# messaging/rabbitmq_message_publisher.py
#

import json

import pika

from app.messaging.exceptions import MessagePublishError
from app.messaging.message_publisher import MessagePublisher


class RabbitMQMessagePublisher(MessagePublisher):
    """
    Implementação de MessagePublisher utilizando RabbitMQ.
    """

    def __init__(self,
                 host: str,
                 port: int,
                 username: str,
                 password: str,
                 queue_name: str) -> None:
        """
        Inicializa o publicador de mensagens do RabbitMQ.

        Args:
            host: Host utilizado para conexão com o RabbitMQ.
            port: Porta utilizada para conexão com o RabbitMQ.
            username: Usuário utilizado para autenticação.
            password: Senha utilizada para autenticação.
            queue_name: Nome da fila utilizada para publicação das mensagens.
        """

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.queue_name = queue_name

    def publish(self, payload: dict) -> None:
        """
        Publica uma mensagem na fila RabbitMQ configurada.

        Args:
            payload: Dados que serão serializados em JSON e publicados
                na fila.

        Returns:
            None.

        Raises:
            MessagePublishError: Caso ocorra uma falha durante a serialização,
                conexão ou publicação da mensagem no RabbitMQ.
        """

        connection = None

        try:
            # Cria as credenciais utilizadas pelo protocolo AMQP para
            # autenticar a conexão no RabbitMQ.
            credentials = pika.PlainCredentials(
                self.username,
                self.password
            )

            # Reúne o endereço do broker e as credenciais que serão usados
            # para estabelecer a conexão AMQP.
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials
            )

            # Serializa o payload para JSON e o converte em bytes, formato
            # utilizado como corpo da mensagem pelo RabbitMQ.
            body = json.dumps(payload).encode('utf-8')

            # Abre uma conexão síncrona com o broker e cria um canal lógico
            # para executar as operações de mensageria.
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            # Garante que a fila exista antes da publicação. A declaração é
            # idempotente quando nome e propriedades permanecem iguais.
            channel.queue_declare(
                queue=self.queue_name,
                durable=True
            )

            # Confirma que o broker aceitou a mensagem publicada.
            channel.confirm_delivery()

            # Publica a mensagem diretamente na fila por meio do exchange
            # padrão. A mensagem é persistente e deve possuir uma rota válida.
            channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=body,
                properties=pika.BasicProperties(
                    content_type='application/json',
                    delivery_mode=2,
                ),
                mandatory=True
            )
        except (
            TypeError,
            ValueError,
            pika.exceptions.AMQPError,
            OSError,
        ) as ex:
            raise MessagePublishError(
                'Unable to publish message to RabbitMQ.'
            ) from ex
        finally:
            if connection is not None and connection.is_open:
                connection.close()
