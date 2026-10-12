#
# exceptions/checkout_exceptions.py
#


class CheckoutChangedError(Exception):
    """
    Indica que os dados atuais do checkout diferem dos apresentados ao
    usuário antes da confirmação.
    """
    pass
