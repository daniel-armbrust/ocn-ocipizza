#
# fn-password-recovery-email/modules/utils.py
#

import string
import secrets
from datetime import datetime

# Globals
TOKEN_LEN = 22
EXPIRATION_SECS = 600 # 10 minutos

def get_token() -> str:
    """Retorna um token aleatório."""
    chars = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(chars) for _ in range(TOKEN_LEN))

    return token

def get_expiration_ts() -> int:
        """Retorna um timestamp que representa uma data de expiração futura."""
        expiration_ts = int(datetime.now().timestamp())
        expiration_ts += EXPIRATION_SECS

        return expiration_ts