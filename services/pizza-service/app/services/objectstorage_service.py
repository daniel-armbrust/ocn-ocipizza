#
# services/objectstorage_service.py
#

from functools import lru_cache
from io import BytesIO
from urllib.parse import urlparse

import oci
from minio import Minio

from app.config.settings import settings


class ObjectStorageService:
    """
    Serviço responsável pelas operações relacionadas aos objetos
    armazenados no Object Storage.

    Em ambiente de desenvolvimento, utiliza MinIO.

    Nos demais ambientes, utiliza OCI Object Storage com
    autenticação via Instance Principal.
    """

    def __init__(self) -> None:
        """
        Inicializa o cliente de Object Storage correspondente
        ao ambiente da aplicação.

        Raises:
            ValueError: Caso alguma configuração obrigatória não esteja
                definida.
        """

        if not settings.objectstorage_bucket:
            raise ValueError('OBJECTSTORAGE_BUCKET is required.')

        self.bucket = settings.objectstorage_bucket

        self.endpoint = None
        self.namespace = None
        self.region = None
        self.client = None

        # Em desenvolvimento, utiliza MinIO.
        if settings.app_env == 'development':
            if not settings.objectstorage_access_key:
                raise ValueError(
                    'OBJECTSTORAGE_ACCESS_KEY is required '
                    'in development environment.'
                )

            if not settings.objectstorage_secret_key:
                raise ValueError(
                    'OBJECTSTORAGE_SECRET_KEY is required '
                    'in development environment.'
                )

            endpoint = urlparse(settings.objectstorage_endpoint)

            self.endpoint = settings.objectstorage_endpoint.rstrip('/')

            # Inicializa o cliente MinIO utilizando o endpoint
            # configurado para o ambiente de desenvolvimento.
            self.client = Minio(
                endpoint.netloc,
                access_key=settings.objectstorage_access_key,
                secret_key=settings.objectstorage_secret_key,
                secure=endpoint.scheme == 'https'
            )

            return

        # Fora do ambiente de desenvolvimento, o namespace
        # do OCI Object Storage é obrigatório.
        if not settings.objectstorage_namespace:
            raise ValueError(
                'OBJECTSTORAGE_NAMESPACE is required '
                'outside development environment.'
            )

        self.namespace = settings.objectstorage_namespace

        # Utiliza Instance Principal para autenticação e obtenção
        # automática da região onde a aplicação está executando.
        signer = (
            oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        )

        self.region = signer.region

        if not self.region:
            raise ValueError(
                'Unable to determine OCI region '
                'from Instance Principal.'
            )

        # Inicializa o cliente OCI Object Storage.
        self.client = oci.object_storage.ObjectStorageClient(
            config={'region': self.region},
            signer=signer
        )

    def get_object_url(self, object_name: str) -> str:
        """
        Retorna a URL completa de um objeto.

        Em desenvolvimento, utiliza o endpoint do MinIO.

        Nos demais ambientes, utiliza a URL regional do
        OCI Object Storage.

        Args:
            object_name: Nome do objeto armazenado no bucket.

        Returns:
            URL completa do objeto.
        """

        # Armazenamento local baseado em MinIO.
        if settings.app_env == 'development':
            return (
                f'{self.endpoint}/'
                f'{self.bucket}/'
                f'{object_name}'
            )

        # No OCI, constrói a URL utilizando região, namespace,
        # bucket e nome do objeto.
        return (
            f'https://objectstorage.{self.region}.oraclecloud.com/'
            f'n/{self.namespace}/'
            f'b/{self.bucket}/'
            f'o/{object_name}'
        )

    def delete_object(self, object_name: str) -> None:
        """
        Remove um objeto do armazenamento configurado.

        Args:
            object_name: Nome do objeto que será removido.
        """

        if settings.app_env == 'development':
            self.client.remove_object(self.bucket, object_name)
            return

        # No OCI, remove o objeto utilizando namespace, bucket
        # e nome do objeto.
        self.client.delete_object(
            namespace_name=self.namespace,
            bucket_name=self.bucket,
            object_name=object_name
        )

    def upload_object(self,
                      object_name: str,
                      data: bytes,
                      content_type: str) -> None:
        """
        Envia um novo objeto para o armazenamento configurado.

        Args:
            object_name: Nome do objeto que será armazenado.
            data: Conteúdo binário do objeto.
            content_type: Tipo MIME do objeto.
        """

        if settings.app_env == 'development':
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=BytesIO(data),
                length=len(data),
                content_type=content_type
            )

            return

        # No OCI, envia o objeto utilizando namespace, bucket
        # e nome do objeto.
        self.client.put_object(
            namespace_name=self.namespace,
            bucket_name=self.bucket,
            object_name=object_name,
            put_object_body=data,
            content_type=content_type
        )


@lru_cache
def get_objectstorage_service() -> ObjectStorageService:
    """
    Fornece o serviço responsável pela integração com Object Storage.
    """

    return ObjectStorageService()
