#
# repositories/orm/__init__.py
#

"""
Registro dos modelos ORM do serviço.

Este módulo garante que todos os modelos SQLAlchemy sejam carregados
antes da configuração dos mappers.
"""

from app.repositories.orm.user_orm import UserORM
from app.repositories.orm.user_email_confirmation_token_orm import UserEmailConfirmationTokenORM
from app.repositories.orm.user_password_reset_token_orm import UserPasswordResetTokenORM
from app.repositories.orm.user_password_history_orm import UserPasswordHistoryORM
from app.repositories.orm.user_refresh_token_orm import UserRefreshTokenORM


__all__ = [
    'UserORM',
    'RefreshTokenORM',
    'UserEmailConfirmationTokenORM',
    'UserPasswordResetTokenORM',
    'UserPasswordHistoryORM',
    'UserRefreshTokenORM'
]