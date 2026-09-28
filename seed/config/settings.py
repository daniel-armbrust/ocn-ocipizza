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
    environment: str = os.getenv("ENVIRONMENT", "development")

    # OCI
    oci_region: str = os.getenv("OCI_REGION", "sa-saopaulo-1")

    # Oracle NoSQL
    nosql_endpoint: str = os.getenv("OCI_NOSQL_ENDPOINT", "http://localhost:18080")
    nosql_compartment_id: str = os.getenv("OCI_NOSQL_COMPARTMENT_ID", "")
    pizza_table_name: str = os.getenv("OCI_NOSQL_TABLE", "pizzas")

    # Object Storage
    object_storage_endpoint: str = os.getenv("OBJECT_STORAGE_ENDPOINT", "http://localhost:9000")
    object_storage_namespace: str = os.getenv("OBJECT_STORAGE_NAMESPACE", "")
    object_storage_access_key: str = os.getenv("OBJECT_STORAGE_ACCESS_KEY", "minioadmin")
    object_storage_secret_key: str = os.getenv("OBJECT_STORAGE_SECRET_KEY", "minioadmin")

    # Pizza Service
    object_storage_pizza_bucket: str = os.getenv("OBJECT_STORAGE_PIZZA_BUCKET", "pizza-images")
    pizza_seed_path: str = os.getenv("PIZZA_SEED_PATH", "seed/pizzas")

    # MySQL
    mysql_host: str = os.getenv("MYSQL_HOST", "localhost")
    mysql_port: int = int(os.getenv("MYSQL_PORT", "3306"))

    mysql_root_user: str = os.getenv("MYSQL_ROOT_USER", "root")
    mysql_root_password: str = os.getenv("MYSQL_ROOT_PASSWORD", "root")

    mysql_database: str = os.getenv("MYSQL_DATABASE", "users")

    mysql_user: str = os.getenv("MYSQL_USER", "user_service")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "user_service" )

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
