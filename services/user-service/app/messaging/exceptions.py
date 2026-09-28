#
# messaging/exceptions.py
#

class MessagePublishError(Exception):
    """
    Exceção lançada quando ocorre uma falha ao publicar uma 
    mensagem no mecanismo de mensageria.
    """
    pass