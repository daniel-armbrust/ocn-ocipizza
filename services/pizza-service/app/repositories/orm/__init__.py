#
# repositories/orm/__init__.py
#

"""
Registro dos modelos ORM do serviço.

Este módulo garante que todos os modelos SQLAlchemy sejam carregados
antes da configuração dos mappers.
"""

from app.repositories.orm.pizza_orm import PizzaORM


__all__ = [
    'PizzaORM'
]