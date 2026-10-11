#
# utils/utils.py
#

from datetime import datetime, timezone
from uuid import UUID
import re


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


def normalize_zip_code(zip_code: str) -> str: 
    """ 
    Normaliza e valida um CEP. 
    
    Args: 
        zip_code: CEP que será normalizado. 
    
    Returns: 
        CEP contendo somente os oito dígitos numéricos. 
    
    Raises: 
        ValueError: Quando o CEP possui formato inválido.
    """ 
    # Remove caracteres de formatação, como o hífen, mantendo somente dígitos. 
    normalized_zip_code = re.sub(r'\D', '', zip_code) 
    
    # CEPs brasileiros devem possuir exatamente oito dígitos. 
    if len(normalized_zip_code) != 8: 
        raise ValueError('Invalid zip code.') 
    
    return normalized_zip_code