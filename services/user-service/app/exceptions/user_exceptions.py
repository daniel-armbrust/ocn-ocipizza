#
# exceptions/user_exceptions.py
#

class UserAlreadyExistsError(Exception):
    """
    Exceção lançada quando já existe um usuário com os dados
    que devem ser únicos, como e-mail ou WhatsApp.
    """
    pass


class UserNotFoundError(Exception):
    """
    Exceção lançada quando o usuário solicitado não é encontrado.
    """
    pass


class UserCreationError(Exception):
    """
    Exceção lançada quando ocorre uma falha ao criar o usuário.
    """
    pass


class UserUpdateError(Exception):
    """
    Exceção lançada quando ocorre uma falha ao atualizar o usuário.
    """
    pass


class UserDeletionError(Exception):
    """
    Exceção lançada quando ocorre um erro ao excluir o usuário.
    """
    pass


class UserEmailPublishError(Exception):
    """
    Exceção lançada quando não é possível publicar uma solicitação
    de envio de e-mail relacionada ao usuário.
    """
    pass