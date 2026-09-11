import os

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return False

load_dotenv()

class Settings:
    """
    Configurações utilizadas pelos scripts de seed.
    """

    # Ambiente
    environment: str = os.getenv(
        "ENVIRONMENT",
        "development"
    )

    # OCI
    oci_region: str = os.getenv(
        "OCI_REGION",
        "sa-saopaulo-1"
    )

    # Oracle NoSQL
    nosql_endpoint: str = os.getenv(
        "OCI_NOSQL_ENDPOINT",
        "http://localhost:18080"
    )

    pizza_table_name: str = os.getenv(
        "OCI_NOSQL_TABLE",
        "pizzas"
    )

    nosql_compartment_id: str = os.getenv(
        "OCI_NOSQL_COMPARTMENT_ID",
        ""
    )

    # Object Storage
    object_storage_endpoint: str = os.getenv(
        "OBJECT_STORAGE_ENDPOINT",
        "http://localhost:9000"
    )

    object_storage_bucket: str = os.getenv(
        "OBJECT_STORAGE_BUCKET",
        "pizza-images"
    )

    object_storage_namespace: str = os.getenv(
        "OBJECT_STORAGE_NAMESPACE",
        ""
    )

    object_storage_access_key: str = os.getenv(
        "OBJECT_STORAGE_ACCESS_KEY",
        "minioadmin"
    )

    object_storage_secret_key: str = os.getenv(
        "OBJECT_STORAGE_SECRET_KEY",
        "minioadmin"
    )

    # Seed
    seed_path: str = os.getenv(
        "SEED_PATH",
        "seed/pizzas"
    )

    @property
    def is_production(self) -> bool:
        """
        Retorna se o seed está executando em produção.
        """

        return self.environment == "production"


    @property
    def is_development(self) -> bool:
        """
        Retorna se o seed está executando em desenvolvimento.
        """

        return self.environment == "development"


settings = Settings()
