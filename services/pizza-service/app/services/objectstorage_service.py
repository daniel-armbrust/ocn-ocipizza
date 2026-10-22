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
        Inicializa o cliente de Object Storage correspondente ao 
        provider configurado para a aplicação. 
        
        Raises: 
            ValueError: Caso alguma configuração obrigatória não esteja 
                definida ou alguma opção configurada não seja suportada. 
        """

        self.bucket = settings.objectstorage_bucket 
        
        self.namespace = None
        self.endpoint = None
        self.region = None
        self.client = None

        # Utiliza o MinIO como implementação local compatível 
        # com armazenamento de objetos.
        if settings.objectstorage_provider == 'minio':
            if not settings.objectstorage_access_key:
                raise ValueError(
                    'OBJECTSTORAGE_ACCESS_KEY is required when ' 
                    'OBJECTSTORAGE_PROVIDER is minio.'
                )

            if not settings.objectstorage_secret_key:
                raise ValueError(
                    'OBJECTSTORAGE_SECRET_KEY is required when ' 
                    'OBJECTSTORAGE_PROVIDER is minio.'
                )

            if not settings.objectstorage_endpoint:
                raise ValueError(
                    'OBJECTSTORAGE_ENDPOINT is required when '
                    'OBJECTSTORAGE_PROVIDER is minio.'
                )

            endpoint = urlparse(settings.objectstorage_endpoint)
            self.endpoint = settings.objectstorage_endpoint.rstrip('/')

            # Inicializa o cliente MinIO utilizando o endpoint 
            # e as credenciais configuradas para execução local.
            self.client = Minio(
                endpoint.netloc,
                access_key=settings.objectstorage_access_key,
                secret_key=settings.objectstorage_secret_key,
                secure=endpoint.scheme == 'https'
            )

            return
        
        # Utiliza o OCI Object Storage como backend de armazenamento.
        elif settings.objectstorage_provider == 'oci':
               
            # Utiliza o arquivo de configuração OCI para autenticação, 
            # normalmente durante a execução local da aplicação.
            if settings.oci_auth_mode == 'config_file':

                if not settings.oci_region:
                    raise ValueError(
                        'OCI_REGION is required to configure regional OCI access '
                        'and build service URLs.'
                    )

                config = oci.config.from_file(
                    file_location=settings.oci_config_file,
                    profile_name=settings.oci_config_profile
                )

                # Obtém a região a partir do arquivo de configuração.
                self.region = settings.oci_region
                config['region'] = settings.oci_region

                self.client = oci.object_storage.ObjectStorageClient(
                    config=config
                )

            # Utiliza a identidade da própria Compute Instance para 
            # autenticação, evitando o uso de chaves e credenciais 
            # armazenadas localmente.
            elif settings.oci_auth_mode == 'instance_principal':
                signer = oci.auth.signers.InstancePrincipalSecurityTokenSigner()

                # Obtém a região automaticamente com base na localidade 
                # em que a aplicação está sendo executada no OCI.
                self.region = signer.region

                self.client = (
                    oci.object_storage.ObjectStorageClient(
                        config={
                            'region': self.region
                        },
                        signer=signer
                    )
                )

            else:
                raise ValueError(
                    'Unsupported OCI authentication mode: '
                    f'{settings.oci_auth_mode}'
                )

            # Obtém automaticamente o namespace associado ao tenant
            # utilizado durante a autenticação no OCI.
            self.namespace = self.client.get_namespace().data

        else:
            raise ValueError(
                'Unsupported Object Storage provider: ' 
                f'{settings.objectstorage_provider}'
            )       

    def get_object(self,
                   object_name: str) -> tuple[bytes, str]:
        """
        Obtém um objeto armazenado no provider configurado.

        Args:
            object_name: Nome do objeto armazenado no bucket.

        Returns:
            Conteúdo binário do objeto e seu tipo MIME.
        """

        # Obtém o objeto armazenado no MinIO.
        if settings.objectstorage_provider == 'minio':
            response = self.client.get_object(
                bucket_name=self.bucket,
                object_name=object_name
            )

            try: 
                content = response.read() 
                content_type = response.headers.get('Content-Type') 
            finally: 
                response.close() 
                response.release_conn()

        # Obtém a imagem armazenada no OCI Object Storage. 
        if settings.objectstorage_provider == 'oci': 
            response = self.client.get_object(
                namespace_name=self.namespace, 
                bucket_name=self.bucket, 
                object_name=object_name
            ) 
            
            content = response.data.content 
            content_type = response.headers.get('content-type')

        # Garante que somente objetos do tipo imagem sejam 
        # retornados pelo serviço. 
        if not content_type or not content_type.startswith('image/'): 
            raise ValueError('Stored object is not a valid image.')

        return content, content_type
            
    def delete_object(self, object_name: str) -> None:
        """
        Remove um objeto do armazenamento configurado.

        Args:
            object_name: Nome do objeto que será removido.
        """

        if settings.objectstorage_provider == 'minio':
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
        Envia uma imagem para o provider de armazenamento configurado.

        Args:
            object_name: Nome utilizado para identificar o objeto.
            data: Conteúdo binário da imagem que será armazenada.
            content_type: Tipo MIME da imagem enviada.

        Raises:
            ValueError: Quando o conteúdo informado não for uma imagem.
            RuntimeError: Quando o provider configurado não for suportado.
        """

        # Garante que somente arquivos do tipo imagem sejam
        # armazenados pelo serviço.
        if not content_type.startswith('image/'):
            raise ValueError(
                'Object content type must be an image.'
            )

        # Envia a imagem para o MinIO.
        if settings.objectstorage_provider == 'minio':
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=BytesIO(data),
                length=len(data),
                content_type=content_type
            )

            return

        # Envia a imagem para o OCI Object Storage utilizando
        # o namespace e o bucket configurados para a aplicação.
        if settings.objectstorage_provider == 'oci':
            self.client.put_object(
                namespace_name=self.namespace,
                bucket_name=self.bucket,
                object_name=object_name,
                put_object_body=data,
                content_type=content_type
            )

            return

        raise RuntimeError(
            'Unsupported Object Storage provider: '
            f'{settings.objectstorage_provider}'
        )


@lru_cache
def get_objectstorage_service() -> ObjectStorageService:
    """
    Fornece o serviço responsável pela integração com Object Storage.
    """

    return ObjectStorageService()
