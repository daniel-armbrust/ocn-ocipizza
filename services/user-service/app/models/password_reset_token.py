#
# models/password_reset_token.py
#

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class PasswordResetToken:
    """
    Representa um token utilizado no processo de redefinição
    da senha de um usuário.

    O token original não é armazenado no banco de dados. Apenas
    seu hash é persistido para permitir a validação posterior
    sem expor o valor enviado ao usuário.

    Attributes:
        id: Identificador interno do registro do token.
        user_id: Identificador UUID do usuário associado ao token.
        token_hash: Hash criptográfico do token de redefinição.
        created_at: Data e hora de criação do token.
        expires_at: Data e hora de expiração do token.
        used_at: Data e hora em que o token foi utilizado.
        revoked_at: Data e hora em que o token foi revogado.
    """

    id: int | None
    user_id: UUID
    token_hash: str
    created_at: datetime
    expires_at: datetime
    used_at: datetime | None = None
    revoked_at: datetime | None = None