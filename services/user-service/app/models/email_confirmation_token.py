#
# models/email_confirmation_token.py
#

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass 
class EmailConfirmationToken: 
    """
    Representa um token utilizado para confirmação do e-mail de um usuário. 
    """ 
    
    id: int | None 
    user_id: UUID 
    token_hash: str 
    created_at: datetime 
    expires_at: datetime 
    used_at: datetime | None = None 
    revoked_at: datetime | None = None
