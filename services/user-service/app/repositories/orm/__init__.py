#
# repositories/orm/__init__.py
#

"""
Registro dos modelos ORM do serviço.

Este módulo garante que todos os modelos SQLAlchemy sejam carregados
antes da configuração dos mappers.
"""

from app.repositories.orm.user_orm import UserORM
from app.repositories.orm.refresh_token_orm import RefreshTokenORM
from app.repositories.orm.email_confirmation_token_orm import EmailConfirmationTokenORM
from app.repositories.orm.password_reset_token_orm import PasswordResetTokenORM
from app.repositories.orm.password_history_orm import PasswordHistoryORM


__all__ = [
    'UserORM',
    'RefreshTokenORM',
    'EmailConfirmationTokenORM',
    'PasswordResetTokenORM',
    'PasswordHistoryORM',
]