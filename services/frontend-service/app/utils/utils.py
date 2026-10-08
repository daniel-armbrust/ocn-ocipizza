#
# utils/utils.py
#

import re

from typing import Any


def normalize_whatsapp(value: Any) -> str:
    """
    Remove caracteres de formatação do número de WhatsApp.

    Args:
        value: Número recebido pelo formulário HTML.

    Returns:
        Número contendo somente dígitos.
    """

    return re.sub(r'\D', '', str(value or ''))


def normalize_optional_string(value: str | None) -> str | None:
    """
    Converte strings vazias em `None`.
    """

    return value or None


def normalize_optional_bool(value: str | None) -> bool | None:
    """
    Converte os valores textuais `true` e `false`
    para booleanos.
    """

    return {
        'true': True,
        'false': False,
    }.get(value or '')