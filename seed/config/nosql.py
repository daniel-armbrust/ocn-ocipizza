import logging

from config.settings import settings


def configure_logger(config):
    logger = logging.getLogger("oci-pizza-seed-nosql")
    logger.addHandler(logging.NullHandler())
    config.set_logger(logger)

    return config


def get_nosql_handle():
    """
    Cria o handle do Oracle NoSQL para o seed.
    """

    from borneo import NoSQLHandle, NoSQLHandleConfig, Regions
    from borneo.iam import SignatureProvider
    from borneo.kv import StoreAccessTokenProvider

    if settings.is_development:
        provider = StoreAccessTokenProvider()

        config = NoSQLHandleConfig(
            settings.nosql_endpoint,
            provider,
        )

        return NoSQLHandle(configure_logger(config))

    region = Regions.from_region_id(settings.oci_region)

    provider = SignatureProvider.create_with_instance_principal(
        region=region,
    )

    config = NoSQLHandleConfig(region, provider,)
    config.set_default_compartment(settings.nosql_compartment_id)

    return NoSQLHandle(configure_logger(config))
