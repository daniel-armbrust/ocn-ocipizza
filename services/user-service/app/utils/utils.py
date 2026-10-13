#
# utils/utils.py
#

from datetime import datetime, timezone
import re
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


def normalize_zip_code(zip_code: str) -> str:
    """
    Normaliza e valida um CEP para uso interno e persistência.

    Args:
        zip_code: CEP com ou sem caracteres de apresentação.

    Returns:
        CEP contendo exatamente oito dígitos.

    Raises:
        ValueError: Quando o valor não resultar em oito dígitos.
    """

    normalized_zip_code = re.sub(r'\D', '', str(zip_code or ''))

    if len(normalized_zip_code) != 8:
        raise ValueError('O CEP deve conter oito dígitos.')

    return normalized_zip_code


def now_utc() -> datetime:
    """
    Retorna a data e hora atual em UTC.

    Returns:
        Data e hora atual com timezone UTC.
    """
    return datetime.now(timezone.utc)


def ensure_utc(value: datetime) -> datetime:
    """
    Normaliza uma data e hora para UTC com informação de timezone.

    O MySQL pode devolver valores ``DATETIME`` sem timezone mesmo quando a
    coluna SQLAlchemy declara ``timezone=True``. Nesses casos, o valor
    persistido pelo serviço já representa UTC e recebe explicitamente esse
    timezone ao retornar para o domínio.

    Args:
        value: Data e hora que deve ser normalizada.

    Returns:
        Data e hora equivalente com timezone UTC.
    """

    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


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
