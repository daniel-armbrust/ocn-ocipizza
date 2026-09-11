from __future__ import annotations

import os
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional


_TABLE_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class Settings:
    environment: str
    oci_region: str
    nosql_endpoint: Optional[str]
    nosql_table: str
    nosql_compartment_id: Optional[str]
    oci_config_file: str
    oci_config_profile: str

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


def _getenv(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name)
    
    if value is None or value == "":
        return default

    return value


@lru_cache
def get_settings() -> Settings:
    table_name = _getenv("OCI_NOSQL_TABLE", "pizzas")

    if table_name is None or _TABLE_NAME_PATTERN.match(table_name) is None:
        raise ValueError("OCI_NOSQL_TABLE must be a valid NoSQL table name")

    return Settings(
        environment=_getenv("ENVIRONMENT", "development") or "development",
        
        nosql_endpoint=_getenv("OCI_NOSQL_ENDPOINT"),
        nosql_table=table_name,
        nosql_compartment_id=_getenv("OCI_NOSQL_COMPARTMENT_ID"),

        oci_region=_getenv("OCI_REGION", "sa-saopaulo-1") or "sa-saopaulo-1",
        oci_config_file=_getenv("OCI_CONFIG_FILE", "~/.oci/config") or "~/.oci/config",
        oci_config_profile=_getenv("OCI_CONFIG_PROFILE", "DEFAULT") or "DEFAULT",
    )
