from functools import lru_cache
import logging

import oci
from oci.auth.signers import InstancePrincipalsSecurityTokenSigner, KeyPairSigner
from oci.nosql import NosqlClient

from app.config.settings import Settings, get_settings
from app.repositories.pizza_repository import (
    LocalNoSqlPizzaRepository,
    NoSqlPizzaRepository,
    PizzaRepository,
)
from app.services.pizza_service import PizzaService


class LocalNoSqlSigner(KeyPairSigner):
    """
    Signer sem autenticação para o endpoint local do Oracle NoSQL em development.
    """

    def __init__(self) -> None:
        """Inicializa o signer local sem credenciais."""

        pass

    def __call__(self, request):
        """Retorna a requisição sem aplicar assinatura."""

        return request


def configure_local_nosql_logger(config):
    """Configura logger silencioso para o client local do Oracle NoSQL."""

    logger = logging.getLogger("oci-pizza-service-nosql")
    logger.addHandler(logging.NullHandler())
    config.set_logger(logger)

    return config


@lru_cache
def get_local_nosql_handle():
    """Cria o handle local do Oracle NoSQL usado em desenvolvimento."""

    from borneo import NoSQLHandle, NoSQLHandleConfig
    from borneo.kv import StoreAccessTokenProvider

    settings = get_settings()
    config = NoSQLHandleConfig(
        settings.nosql_endpoint,
        StoreAccessTokenProvider(),
    )

    return NoSQLHandle(configure_local_nosql_logger(config))


@lru_cache
def get_nosql_client() -> NosqlClient:
    """Cria o client Oracle NoSQL conforme o ambiente configurado."""

    settings = get_settings()

    if settings.is_development and settings.nosql_endpoint is not None:
        return NosqlClient(
            {"region": settings.oci_region},
            signer=LocalNoSqlSigner(),
            service_endpoint=settings.nosql_endpoint,
        )

    if settings.is_development:
        config = oci.config.from_file(
            file_location=settings.oci_config_file,
            profile_name=settings.oci_config_profile,
        )
        config["region"] = settings.oci_region
        return NosqlClient(
            config,
            service_endpoint=settings.nosql_endpoint,
        )

    signer = InstancePrincipalsSecurityTokenSigner()
    return NosqlClient(
        {"region": settings.oci_region},
        signer=signer,
    )


@lru_cache
def get_pizza_repository() -> PizzaRepository:
    """Disponibiliza o repositório de pizzas adequado ao ambiente."""

    settings = get_settings()

    if settings.is_development and settings.nosql_endpoint is not None:
        return LocalNoSqlPizzaRepository(
            get_local_nosql_handle(),
            settings.nosql_table,
        )

    return NoSqlPizzaRepository(get_nosql_client(), settings)


def get_pizza_service() -> PizzaService:
    """Monta o serviço de pizzas com seu repositório configurado."""

    return PizzaService(get_pizza_repository())
