#
# messaging/message_consumer.py
#

from abc import ABC, abstractmethod

class MessageConsumer(ABC):
    """
    Define as operações necessárias para consumo de mensagens
    provenientes de uma fila.
    """

    @abstractmethod
    def receive(self) -> list[dict]:
        """
        Recebe mensagens disponíveis na fila.

        Returns:
            Lista contendo as mensagens recebidas.
        """
        pass

    @abstractmethod
    def delete(self, receipt: str) -> None:
        """
        Remove uma mensagem da fila após seu processamento.

        Args:
            receipt: Identificador utilizado para confirmar a remoção
                da mensagem da fila.
        """
        pass