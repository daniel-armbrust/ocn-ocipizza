#
# config/logging.py
#

import logging
import sys
from datetime import datetime, timezone
from uuid import uuid4

import oci

from oci.loggingingestion import LoggingClient

from oci.loggingingestion.models import (
    LogEntry,
    LogEntryBatch,
    PutLogsDetails
)

from app.config.settings import settings


class OciLoggingHandler(logging.Handler):
    """
    Handler responsável por enviar logs da aplicação para o
    OCI Logging através da Logging Ingestion API.

    A autenticação é realizada utilizando Instance Principal.
    """

    def __init__(self, log_id: str, source: str) -> None:
        """
        Inicializa o handler OCI Logging.

        Args:
            log_id: OCID do Custom Log utilizado para ingestão.
            source: Identificação da origem das mensagens de log.
        """

        super().__init__()

        signer = (
            oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        )

        self.client = LoggingClient(
            config={},
            signer=signer
        )

        self.log_id = log_id
        self.source = source

    def emit(self, record: logging.LogRecord) -> None:
        """
        Envia uma mensagem de log para o OCI Logging.

        Args:
            record: Registro produzido pelo módulo `logging`.
        """

        try:
            message = self.format(record)

            now = datetime.now(timezone.utc)

            log_entry = LogEntry(
                data=message,
                id=str(uuid4()),
                time=now
            )

            log_entry_batch = LogEntryBatch(
                entries=[
                    log_entry,
                ],
                source=self.source,
                type='application',
                subject=record.name,
                defaultlogentrytime=now
            )

            put_logs_details = PutLogsDetails(
                specversion='1.0',
                log_entry_batches=[
                    log_entry_batch
                ]
            )

            self.client.put_logs(
                log_id=self.log_id,
                put_logs_details=put_logs_details
            )

        except Exception:
            self.handleError(record)


def configure_logging() -> None:
    """
    Configura o logging global da aplicação.

    Em ambiente de desenvolvimento, envia os logs para stdout.

    Nos demais ambientes, envia os logs diretamente para o
    OCI Logging utilizando Instance Principal.

    Raises:
        ValueError: Caso o OCID do OCI Logging não esteja configurado
            em ambientes diferentes de desenvolvimento.
    """

    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level.upper())
    root_logger.handlers.clear()

    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s'
    )

    if settings.app_env == 'development':
        handler = logging.StreamHandler(sys.stdout)
    else:
        if not settings.oci_log_id:
            raise ValueError(
                'OCI_LOG_ID is required outside development environment.'
            )

        handler = OciLoggingHandler(
            log_id=settings.oci_log_id,
            source='pizza-service'
        )

    handler.setFormatter(formatter)

    root_logger.addHandler(handler)

