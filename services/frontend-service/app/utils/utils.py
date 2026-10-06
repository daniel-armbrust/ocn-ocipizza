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
