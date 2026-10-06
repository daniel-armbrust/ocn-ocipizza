#
# repositories/redis/connection.py
#

from redis.asyncio import Redis

from app.config.settings import settings

# Mantém uma única instância do cliente Redis durante o ciclo de vida
# da aplicação. O redis-py gerencia internamente um pool de conexões,
# evitando a criação de um novo cliente a cada requisição.
_redis_client: Redis | None = None


def get_redis_client() -> Redis:
    """
    Retorna o cliente Redis compartilhado pela aplicação.

    O cliente é criado sob demanda na primeira utilização e reutilizado
    nas chamadas seguintes. Essa abordagem permite o reaproveitamento
    do pool de conexões mantido internamente pelo redis-py.

    Returns:
        Cliente assíncrono configurado para comunicação com o Redis.

    Raises:
        RuntimeError: Caso o endpoint do Redis não esteja configurado.
    """

    global _redis_client

    if _redis_client is not None:
        return _redis_client

    if not settings.redis_endpoint:
        raise RuntimeError(
            'Redis endpoint is not configured.'
        )

    # decode_responses=True faz com que valores retornados pelo Redis
    # sejam convertidos para str, evitando o tratamento manual de bytes
    # nas implementações dos repositórios.
    _redis_client = Redis.from_url(
        settings.redis_endpoint,
        decode_responses=True
    )

    return _redis_client