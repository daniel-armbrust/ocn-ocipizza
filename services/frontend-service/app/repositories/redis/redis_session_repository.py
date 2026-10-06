#
# repositories/redis/redis_session_repository.py
#

import json
from typing import Any

from redis.asyncio import Redis

from app.repositories.session_repository import SessionRepository


class RedisSessionRepository(SessionRepository):
    """
    Implementa a persistência de sessões utilizando Redis.

    Os dados da sessão são serializados em JSON e armazenados
    utilizando o identificador da sessão como chave.
    """

    def __init__(self, client: Redis) -> None:
        """
        Inicializa o repositório.

        Args:
            client: Cliente assíncrono utilizado para comunicação
                com o Redis.
        """

        self.client = client

    async def create(self,
                     session_id: str,
                     data: dict[str, Any],
                     ttl: int) -> None:
        """
        Cria uma nova sessão no Redis.

        Args:
            session_id: Identificador único da sessão.
            data: Dados associados à sessão.
            ttl: Tempo de validade da sessão, em segundos.
        """

        await self.client.set(
            name=session_id,
            value=json.dumps(data),
            ex=ttl
        )

    async def get(self, session_id: str) -> dict[str, Any] | None:
        """
        Retorna os dados associados a uma sessão.

        Args:
            session_id: Identificador único da sessão.

        Returns:
            Dados da sessão ou `None` caso ela não exista
            ou tenha expirado.
        """

        value = await self.client.get(session_id)

        if value is None:
            return None

        return json.loads(value)

    async def update(self,
                     session_id: str,
                     data: dict[str, Any],
                     ttl: int | None = None) -> None:
        """
        Atualiza os dados associados a uma sessão.

        Quando `ttl` não é informado, mantém o tempo de expiração
        atualmente configurado para a chave.

        Args:
            session_id: Identificador único da sessão.
            data: Novos dados associados à sessão.
            ttl: Novo tempo de validade da sessão, em segundos.
        """

        value = json.dumps(data)

        if ttl is not None:
            await self.client.set(
                name=session_id,
                value=value,
                ex=ttl
            )
            return

        await self.client.set(
            name=session_id,
            value=value,
            keepttl=True
        )

    async def delete(self, session_id: str) -> None:
        """
        Remove uma sessão do Redis.

        Args:
            session_id: Identificador único da sessão.
        """

        await self.client.delete(session_id)

    async def exists(self, session_id: str) -> bool:
        """
        Verifica se uma sessão existe no Redis.

        Args:
            session_id: Identificador único da sessão.

        Returns:
            `True` quando a sessão existir; caso contrário,
            `False`.
        """

        return bool(
            await self.client.exists(
                session_id
            )
        )