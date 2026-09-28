#
# utils/normalization.py
#

from datetime import datetime, timezone
from uuid import UUID


def normalize_email(email: str) -> str:
    """
    Normaliza e-mails para comparação e persistência consistentes.

    Args:
        email: Endereço de e-mail recebido pela aplicação.

    Returns:
        E-mail sem espaços nas bordas e em letras minúsculas.
    """

    return email.strip().lower()


def now_utc() -> datetime:
    """
    Retorna a data e hora atual em UTC.

    Returns:
        Data e hora atual com timezone UTC.
    """
    return datetime.now(timezone.utc)

def uuid_to_bin(value: UUID) -> bytes: 
    """
    Converte um UUID para sua representação binária de 16 bytes. 
    
    Args: 
        value: UUID a ser convertido. 
    
    Returns: 
        Representação binária do UUID. 
    """ 
    
    return value.bytes 


def bin_to_uuid(value: bytes) -> UUID: 
    """
    Converte uma representação binária de 16 bytes para UUID. 
    
    Args: 
        value: Representação binária do UUID. 
    
    Returns: 
        UUID correspondente ao valor informado. 
    """
    
    return UUID(bytes=value)