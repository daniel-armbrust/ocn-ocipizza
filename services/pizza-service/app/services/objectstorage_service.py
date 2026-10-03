#
# services/objectstorage_service.py
#

import oci

from app.config.settings import settings


import oci

from app.config.settings import settings


class ObjectStorageService:
    """
    Serviço responsável por construir URLs de objetos armazenados
    no Object Storage.

    Em ambiente de desenvolvimento, utiliza o endpoint e o bucket
    configurados para o armazenamento local.

    Nos demais ambientes, utiliza Instance Principal para identificar
    automaticamente a região OCI onde a aplicação está sendo executada.
    """

    def __init__(self) -> None:
        """
        Inicializa o serviço de Object Storage.
        """

        self.signer = None

        # Fora do ambiente de desenvolvimento, utiliza Instance Principal
        # para identificar automaticamente a região OCI da aplicação.
        if settings.app_env != 'development':
            self.signer = (
                oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
            )

    def get_object_url(self, object_name: str) -> str:
        """
        Retorna a URL completa de um objeto.

        Args:
            object_name: Nome do objeto armazenado no bucket.

        Returns:
            URL completa do objeto.

        Raises:
            ValueError: Caso alguma configuração obrigatória não esteja
                definida.
        """

        # Em desenvolvimento, utiliza o endpoint local configurado.
        if settings.app_env == 'development':
            return self._get_development_object_url(object_name)

        # Nos demais ambientes, constrói a URL regional do OCI
        # Object Storage.
        return self._get_oci_object_url(object_name)

    def _get_development_object_url(self, object_name: str) -> str:
        """
        Retorna a URL do objeto no ambiente de desenvolvimento.

        Args:
            object_name: Nome do objeto armazenado no bucket.

        Returns:
            URL completa do objeto.

        Raises:
            ValueError: Caso endpoint ou bucket não estejam configurados.
        """

        # O endpoint representa apenas o endereço base do serviço
        # de armazenamento utilizado no ambiente de desenvolvimento.
        if not settings.objectstorage_endpoint:
            raise ValueError(
                'OBJECTSTORAGE_ENDPOINT is required in development environment.'
            )

        # O nome do bucket é mantido separado do endpoint para reproduzir
        # o mesmo conceito utilizado pelo OCI Object Storage.
        if not settings.objectstorage_bucket:
            raise ValueError(
                'OBJECTSTORAGE_BUCKET is required in development environment.'
            )

        endpoint = settings.objectstorage_endpoint.rstrip('/')

        return (
            f'{endpoint}/'
            f'{settings.objectstorage_bucket}/'
            f'{object_name}'
        )

    def _get_oci_object_url(self, object_name: str) -> str:
        """
        Retorna a URL do objeto armazenado no OCI Object Storage.

        A região utilizada na URL é obtida automaticamente através
        do Instance Principal da instância.

        Args:
            object_name: Nome do objeto armazenado no bucket.

        Returns:
            URL completa do objeto.

        Raises:
            ValueError: Caso namespace, bucket, signer ou região
                não estejam disponíveis.
        """

        # O namespace identifica o espaço de nomes do Object Storage
        # associado à tenancy.
        if not settings.objectstorage_namespace:
            raise ValueError(
                'OBJECTSTORAGE_NAMESPACE is required outside development environment.'
            )

        # O bucket identifica onde as imagens das pizzas estão armazenadas.
        if not settings.objectstorage_bucket:
            raise ValueError(
                'OBJECTSTORAGE_BUCKET is required outside development environment.'
            )

        # O signer é criado no construtor somente fora do ambiente
        # de desenvolvimento.
        if self.signer is None:
            raise ValueError(
                'OCI Instance Principal signer is not available.'
            )

        # A região é descoberta automaticamente através do
        # Instance Principal.
        region = self.signer.region

        if not region:
            raise ValueError(
                'Unable to determine OCI region from Instance Principal.'
            )

        # Constrói a URL pública do objeto utilizando região,
        # namespace, bucket e nome do arquivo.
        return (
            f'https://objectstorage.{region}.oraclecloud.com/'
            f'n/{settings.objectstorage_namespace}/'
            f'b/{settings.objectstorage_bucket}/'
            f'o/{object_name}'
        )


def get_objectstorage_service() -> ObjectStorageService:
    """
    Fornece o serviço responsável pela integração com Object Storage.
    """

    return ObjectStorageService()