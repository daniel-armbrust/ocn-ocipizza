#
# messaging/exceptions.py
#


class MessageConsumeError(Exception):
    """
    Exceção lançada quando ocorre uma falha ao consumir ou confirmar uma
    mensagem no mecanismo de mensageria.
    """
    pass
