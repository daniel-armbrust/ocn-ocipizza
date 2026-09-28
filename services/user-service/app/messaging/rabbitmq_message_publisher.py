#
# messaging/rabbitmq_message_publisher.py
#

import json

import pika

from app.config.settings import settings
from app.messaging.exceptions import MessagePublishError
from app.messaging.message_publisher import MessagePublisher


class RabbitMqMessagePublisher(MessagePublisher):
    """
    Implementação de MessagePublisher utilizando RabbitMQ.
    """

    def __init__(self) -> None:
        """ 
        Inicializa o publicador de mensagens RabbitMQ utilizando 
        as configurações da aplicação. 
        """

        self.host = settings.rabbitmq_host 
        self.port = settings.rabbitmq_port 
        self.username = settings.rabbitmq_username 
        self.password = settings.rabbitmq_password 
        self.queue_name = settings.rabbitmq_queue_name

    def publish(self, payload: dict) -> None:
        """ 
        Publica uma mensagem na fila RabbitMQ configurada. 
        
        Args: 
            payload: Dados que serão serializados em JSON e publicados 
                na fila. 
        
        Returns: 
            None. 
        
        Raises: 
            MessagePublishError: Caso ocorra uma falha durante a conexão 
                ou publicação da mensagem no RabbitMQ. 
        """

        # Cria as credenciais utilizadas para autenticação no RabbitMQ.
        credentials = pika.PlainCredentials(self.username, self.password)

        # Define os parâmetros necessários para estabelecer a conexão 
        # com o broker RabbitMQ.
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials
        )

        # Converte o dicionário Python para JSON e depois para bytes, 
        # formato utilizado para envio da mensagem ao RabbitMQ.
        body = json.dumps(payload).encode('utf-8')

        # A conexão começa como None para permitir seu fechamento seguro 
        # no bloco finally, mesmo que a conexão não seja estabelecida.
        connection = None

        try:
            # Estabelece uma conexão TCP/AMQP com o broker RabbitMQ. 
            connection = pika.BlockingConnection(parameters)

            # Cria um canal lógico dentro da conexão. 
            # As operações de mensageria são realizadas através do channel. 
            channel = connection.channel()

            # Garante que a fila exista antes da publicação. 
            # durable=True faz com que a definição da fila sobreviva 
            # a reinicializações do RabbitMQ.
            channel.queue_declare(queue=self.queue_name, durable=True)

            # Habilita publisher confirms. 
            # Com isso, o publisher pode detectar falhas na aceitação 
            # da mensagem pelo broker.
            channel.confirm_delivery()

            # Publica a mensagem na fila. 
            channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=body,

                properties=pika.BasicProperties(
                    content_type='application/json', 
                    # Marca a mensagem como persistente.
                    delivery_mode=2   
                ),

                # Solicita erro caso a mensagem não possa ser roteada 
                # para nenhuma fila.
                mandatory=True
            )

        except (pika.exceptions.AMQPError, OSError) as ex:
            raise MessagePublishError('Unable to publish message to RabbitMQ.') from ex
        
        finally:
            if connection is not None and connection.is_open:
                connection.close()