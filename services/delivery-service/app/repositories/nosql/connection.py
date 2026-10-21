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

    if settings.nosql_provider == 'local':
        return _create_local_nosql_handle()
    
    if settings.nosql_provider == 'oci':
        return _create_oci_nosql_handle()
    
    raise ValueError(
        f'Unsupported NoSQL provider: {settings.nosql_provider}'
    )


def _create_local_nosql_handle() -> NoSQLHandle:
    """
    Cria um handle para acesso ao Oracle NoSQL executado localmente.

    Returns:
        Handle configurado para acesso ao Oracle NoSQL local.

    Raises:
        ValueError: Caso o endpoint do Oracle NoSQL não esteja definido.
    """

    if not settings.nosql_endpoint:
        raise ValueError(
            'NOSQL_ENDPOINT is required when NOSQL_PROVIDER is local.'
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


def _create_oci_nosql_handle() -> NoSQLHandle:
    """
    Cria um handle para acesso ao Oracle NoSQL Database Cloud Service.

    Returns:
        Handle configurado para acesso ao OCI NoSQL.

    Raises:
        ValueError: Caso alguma configuração obrigatória não esteja
            definida ou o modo de autenticação não seja suportado.
    """

    region = None  

    # Utiliza o arquivo de configuração OCI para autenticação,
    # normalmente durante a execução local da aplicação.
    if settings.oci_auth_mode == 'config_file':

        if not settings.oci_region:
            raise ValueError(
                'OCI_REGION is required when NOSQL_PROVIDER is oci.'
            )

        if not settings.oci_config_file:
            raise ValueError(
                'OCI_CONFIG_FILE is required when OCI_AUTH_MODE '
                'is config_file.'
            )

        authorization_provider = SignatureProvider(
            config_file=settings.oci_config_file,
            profile_name=settings.oci_config_profile
        )

        region = settings.oci_region

    # Utiliza a identidade da própria Compute Instance para autenticação,
    # evitando o uso de chaves e credenciais armazenadas localmente.
    elif settings.oci_auth_mode == 'instance_principal':
        authorization_provider = (
            SignatureProvider.create_with_instance_principal()
        )

        region = authorization_provider.get_region()

        if not region:
            raise ValueError(
                'Unable to determine OCI region '
                'from Instance Principal.'
            )

    else:
        raise ValueError(
            f'Unsupported OCI authentication mode: '
            f'{settings.oci_auth_mode}'
        )

    if not settings.nosql_compartment_id:
        raise ValueError(
            'NOSQL_COMPARTMENT_ID is required when '
            'NOSQL_PROVIDER is oci.'
        )

    config = (
        NoSQLHandleConfig(region)
        .set_authorization_provider(authorization_provider)
        .set_default_compartment(settings.nosql_compartment_id)
    )

    config.set_logger(
        logging.getLogger('borneo')
    )

    return NoSQLHandle(config)