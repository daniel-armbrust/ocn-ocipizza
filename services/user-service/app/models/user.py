#
# models/user.py
#

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class User:
    """
    Representa um usuário persistido pelo `user-service`.

    Os atributos armazenam dados básicos de perfil, credenciais por hash,
    estado de confirmação de e-mail e controle de desativação da conta.
    """

    id: UUID
    full_name: str
    email: str
    confirmed: bool
    whatsapp: str
    password_hash: str
    created_at: datetime
    updated_at: datetime
    disabled_at: Optional[datetime] = None

    @property
    def active(self) -> bool:
        """
        Indica se o usuário está ativo para autenticação e uso da API.

        Returns:
            `True` quando o usuário não possui data de desativação.
        """

        return self.disabled_at is None