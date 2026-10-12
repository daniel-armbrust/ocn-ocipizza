#
# clients/jwks_client.py
#

import logging
from typing import Any

import httpx

from app.config.settings import settings

logger = logging.getLogger(__name__)


class JwksClient:
    """
    Gerencia a obtenção e o cache das chaves públicas utilizadas
    para validação dos tokens JWT.
    """

    def __init__(self):
        """
        Inicializa o cliente responsável pelas chaves JWKS.
        """

        self._keys: dict[str, dict[str, Any]] = {}

    async def warm_up(self) -> None:
        """
        Tenta carregar antecipadamente as chaves públicas no cache.

        A indisponibilidade do user-service durante a inicialização não
        impede que o delivery-service seja iniciado.
        """

        try:
            await self._refresh()
        except Exception:
            logger.warning(
                'Não foi possível carregar as chaves JWKS durante '
                'a inicialização do serviço.',
                exc_info=True
            )

    async def get_key(self, kid: str) -> dict[str, Any]:
        """
        Obtém uma chave pública pelo identificador.

        Args:
            kid: Identificador da chave pública presente no JWT.

        Returns:
            Chave pública correspondente ao identificador informado.

        Raises:
            RuntimeError: Quando não é possível obter a chave pública.
        """

        # Utiliza primeiro a chave armazenada localmente para evitar
        # chamadas desnecessárias ao user-service.
        key = self._keys.get(kid)

        if key:
            return key

        # Caso a chave não esteja no cache, atualiza o JWKS. Isso também
        # permite recuperar o funcionamento quando o user-service estava
        # indisponível durante a inicialização.
        await self._refresh()

        key = self._keys.get(kid)

        if not key:
            raise RuntimeError(
                f'JWT signing key not found for kid: {kid}'
            )

        return key

    async def _refresh(self) -> None:
        """
        Atualiza o cache local utilizando o endpoint JWKS do user-service.

        Raises:
            httpx.HTTPError: Quando ocorre erro na comunicação HTTP.
            ValueError: Quando a resposta JWKS possui formato inválido.
        """

        async with httpx.AsyncClient(
            timeout=settings.http_client_timeout
        ) as client:
            response = await client.get(
                settings.jwt_jwks_url
            )

        response.raise_for_status()

        data = response.json()
        keys = data.get('keys')

        if not isinstance(keys, list):
            raise ValueError('Invalid JWKS response.')

        # Substitui o cache somente depois de uma resposta JWKS válida,
        # preservando as chaves existentes caso uma atualização falhe.
        self._keys = {
            key['kid']: key
            for key in keys
            if key.get('kid')
        }


# Instância compartilhada responsável por obter e manter em cache
# as chaves públicas utilizadas na validação dos tokens JWT.
jwks_client = JwksClient()