#
# models/user_refresh_token.py
#

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class UserRefreshToken:
    """
    Representa um refresh token associado à sessão de um usuário.

    O refresh token permite obter um novo access token sem exigir
    novamente as credenciais do usuário.

    O token original nunca deve ser armazenado no banco de dados.
    Apenas seu hash é persistido para permitir validação e revogação
    de forma segura.

    Attributes:
        id: Identificador interno do registro do refresh token.
        user_id: Identificador UUID do usuário associado ao token.
        token_hash: Hash criptográfico do refresh token.
        created_at: Data e hora de criação do refresh token.
        expires_at: Data e hora de expiração do refresh token.
        revoked_at: Data e hora em que o refresh token foi revogado.
    """

    id: int | None
    user_id: UUID
    token_hash: str
    created_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None