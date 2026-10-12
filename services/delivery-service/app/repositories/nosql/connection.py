#
# repositories/nosql/connection.py
#

import logging
from collections.abc import Generator

from borneo import NoSQLHandle, NoSQLHandleConfig
from borneo.iam import SignatureProvider
from borneo.kv import StoreAccessTokenProvider

from app.config.settings import settings

logger = logging.getLogger(__name__)


def get_nosql_handle() -> Generator[NoSQLHandle | None, None, None]:
    """
    Fornece um handle compartilhado para acesso ao Oracle NoSQL.

    Yields:
        Handle configurado quando o provider for NoSQL. Para providers
        diferentes, retorna None sem abrir uma conexão.

    Raises:
        ValueError: Caso alguma configuração obrigatória não esteja
            definida.
    """

    if settings.persistence_provider != 'nosql':
        yield None
        return

    handle = create_nosql_handle()

    try:
        yield handle
    finally:
        handle.close()


def create_nosql_handle() -> NoSQLHandle:
    """
    Cria um handle Oracle NoSQL para uso fora da injeção do FastAPI.

    Em ambiente de desenvolvimento, utiliza o Oracle NoSQL local
    configurado por endpoint.

    Nos demais ambientes, utiliza Instance Principal para
    autenticação no Oracle NoSQL Database Cloud Service.

    Returns:
        Handle configurado para acesso ao Oracle NoSQL.

    Raises:
        ValueError: Caso alguma configuração obrigatória não esteja
            definida.
    """

    if settings.app_env == 'development':
        if not settings.nosql_endpoint:
            raise ValueError(
                'NOSQL_ENDPOINT is required in development environment.'
            )

        authorization_provider = StoreAccessTokenProvider()

        config = NoSQLHandleConfig(
            settings.nosql_endpoint
        ).set_authorization_provider(
            authorization_provider
        )

        config.set_logger(
            logging.getLogger('borneo')
        )

        return NoSQLHandle(config)

    if not settings.oci_region:
        raise ValueError(
            'OCI_REGION is required outside development environment.'
        )

    authorization_provider = (
        SignatureProvider.create_with_instance_principal(
            region=settings.oci_region
        )
    )

    config = NoSQLHandleConfig(
        settings.oci_region
    ).set_authorization_provider(
        authorization_provider
    )

    config.set_logger(
        logging.getLogger('borneo')
    )

    return NoSQLHandle(config)
