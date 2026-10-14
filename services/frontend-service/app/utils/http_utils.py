#
# utils/http_utils.py
#

from collections.abc import Collection

import httpx


def get_jsend_error_code(
    ex: httpx.HTTPStatusError,
    supported_codes: Collection[str],
    fallback: str
) -> str:
    """
    Obtém um código funcional conhecido de uma resposta JSend de falha.

    Args:
        ex: Erro HTTP contendo a resposta recebida do microsserviço.
        supported_codes: Códigos reconhecidos pelo frontend-service.
        fallback: Código utilizado quando a resposta não é reconhecida.

    Returns:
        Código funcional conhecido ou o fallback informado.
    """

    try:
        payload = ex.response.json()
    except ValueError:
        return fallback

    if not isinstance(payload, dict):
        return fallback

    data = payload.get('data')

    if not isinstance(data, dict):
        return fallback

    code = data.get('code')

    return (
        code
        if isinstance(code, str) and code in supported_codes
        else fallback
    )
