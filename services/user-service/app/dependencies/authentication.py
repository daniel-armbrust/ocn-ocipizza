#
# dependencies/authentication.py
#

from uuid import UUID


def get_current_user_id() -> UUID:
    """
    Retorna temporariamente o identificador de um usuário de demonstração.
    
    Esta função representa o usuário autenticado durante o desenvolvimento
    funcional da aplicação. A implementação será substituída posteriormente
    pela validação do token JWT e extração do identificador do usuário.
    
    Returns:
        UUID fixo correspondente ao usuário de demonstração Rita de Cássia.
    """

    return UUID('33333333-3333-4333-8333-333333333333')