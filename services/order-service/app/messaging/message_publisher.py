#
# messaging/message_publisher.py
#

from abc import ABC, abstractmethod


class MessagePublisher(ABC):
    """ 
    Define o contrato para publicação de mensagens no mecanismo 
    de mensageria utilizado pela aplicação. 
    """
    
    @abstractmethod
    def publish(self, payload: dict) -> None:
        """
        Publica uma mensagem no mecanismo de mensageria configurado. 
        
        Args: 
            payload: Dados que serão publicados na mensagem. 
        
        Returns: 
            None. 
        
        Raises: 
            MessagePublishError: Caso ocorra uma falha durante a 
                publicação da mensagem. 
        """
        pass