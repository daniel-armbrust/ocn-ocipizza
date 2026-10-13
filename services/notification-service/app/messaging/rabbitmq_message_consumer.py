#
# messaging/rabbitmq_message_consumer.py
#

import json

import pika

from app.messaging.exceptions import MessageConsumeError
from app.messaging.message_consumer import MessageConsumer


class RabbitMQMessageConsumer(MessageConsumer):
    """
    Implementação de MessageConsumer utilizando RabbitMQ.
    """

    def __init__(self,
                 host: str,
                 port: int,
                 username: str,
                 password: str,
                 queue_name: str) -> None:
        """
        Inicializa o consumidor de mensagens do RabbitMQ.

        Args:
            host: Host utilizado para conexão com o RabbitMQ.
            port: Porta utilizada para conexão com o RabbitMQ.
            username: Usuário utilizado para autenticação.
            password: Senha utilizada para autenticação.
            queue_name: Nome da fila utilizada para consumo das mensagens.
        """

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.queue_name = queue_name

        self.connection = None
        self.channel = None

    def receive(self) -> list[dict]:
        """
        Recebe uma mensagem disponível na fila.

        Returns:
            Lista contendo a mensagem recebida ou uma lista vazia
                quando nenhuma mensagem estiver disponível.

        Raises:
            MessageConsumeError: Caso ocorra uma falha durante a conexão,
                leitura ou desserialização da mensagem.
        """

        try:
            self._connect()

            # Realiza uma leitura pontual sem manter um consumidor contínuo
            # registrado no RabbitMQ. A confirmação é feita posteriormente.
            method, _, body = self.channel.basic_get(
                queue=self.queue_name,
                auto_ack=False
            )

            if method is None:
                return []

            try:
                message_body = json.loads(body.decode('utf-8'))
            except (UnicodeDecodeError, json.JSONDecodeError):
                # Uma mensagem inválida não se torna válida em novas tentativas.
                # A rejeição evita bloquear o consumo com prefetch_count igual a 1.
                self.channel.basic_reject(
                    delivery_tag=method.delivery_tag,
                    requeue=False
                )
                raise

            # O delivery_tag identifica a entrega e será utilizado para
            # confirmar o processamento no mesmo canal RabbitMQ.
            return [{
                'receipt': str(method.delivery_tag),
                'body': message_body
            }]
        except (
            TypeError,
            ValueError,
            pika.exceptions.AMQPError,
            OSError,
            RuntimeError
        ) as ex:
            raise MessageConsumeError(
                'Unable to consume message from RabbitMQ.'
            ) from ex

    def delete(self, receipt: str) -> None:
        """
        Confirma o processamento de uma mensagem recebida.

        Args:
            receipt: Identificador da entrega utilizado para confirmar
                o processamento da mensagem.

        Raises:
            MessageConsumeError: Caso o canal da entrega não esteja disponível
                ou a confirmação não possa ser realizada.
        """

        try:
            if not (
                self.connection
                and self.connection.is_open
                and self.channel
                and self.channel.is_open
            ):
                raise RuntimeError(
                    'RabbitMQ channel is not available to acknowledge message.'
                )

            # No RabbitMQ a mensagem não é removida explicitamente. O basic_ack
            # confirma o processamento e permite que o broker a descarte.
            self.channel.basic_ack(
                delivery_tag=int(receipt)
            )
        except (
            TypeError,
            ValueError,
            pika.exceptions.AMQPError,
            OSError,
            RuntimeError
        ) as ex:
            raise MessageConsumeError(
                'Unable to acknowledge RabbitMQ message.'
            ) from ex

    def close(self) -> None:
        """
        Encerra a conexão utilizada pelo consumidor.
        """

        if self.connection and self.connection.is_open:
            self.connection.close()

        self.connection = None
        self.channel = None

    def _connect(self) -> None:
        """
        Estabelece a conexão com o RabbitMQ quando necessário.
        """

        if (
            self.connection
            and self.connection.is_open
            and self.channel
            and self.channel.is_open
        ):
            return

        # Define as credenciais utilizadas para autenticação
        # junto ao servidor RabbitMQ.
        credentials = pika.PlainCredentials(
            self.username,
            self.password
        )

        # Cria a conexão TCP com o RabbitMQ utilizando os parâmetros
        # configurados para o ambiente atual.
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
            )
        )

        self.channel = self.connection.channel()

        # Garante que a fila exista antes de iniciar o consumo.
        # A opção durable permite que a definição da fila sobreviva
        # à reinicialização do RabbitMQ.
        self.channel.queue_declare(
            queue=self.queue_name,
            durable=True,
        )

        # Limita a quantidade de mensagens não confirmadas entregues
        # ao consumidor simultaneamente.
        self.channel.basic_qos(
            prefetch_count=1,
        )
