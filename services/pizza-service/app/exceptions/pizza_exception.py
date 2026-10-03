#
# exceptions/pizza_exception.py
#

class PizzaQueryError(Exception):
    """
    Exceção lançada quando ocorre uma falha durante a consulta
    dos dados de pizzas.
    """
    pass


class PizzaNotFoundError(Exception):
    """
    Exceção lançada quando uma pizza não é encontrada.
    """
    pass


class PizzaCreationError(Exception):
    """
    Exceção lançada quando ocorre uma falha durante o processo
    de criação de uma pizza.
    """
    pass


class PizzaUpdateError(Exception):
    """
    Exceção lançada quando ocorre uma falha durante o processo
    de atualização de uma pizza.
    """
    pass


class PizzaDeletionError(Exception):
    """
    Exceção lançada quando ocorre uma falha durante o processo
    de remoção de uma pizza.
    """
    pass