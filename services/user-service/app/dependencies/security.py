#
# dependencies/security.py
#

import base64
from pathlib import Path

import oci

from app.config.settings import settings
from app.services.jwt_service import JwtService
from app.services.token_service import TokenService
from app.dependencies.oci_credentials import get_oci_credentials


def get_jwt_service() -> JwtService:
    """
    Fornece o serviço responsável pela geração e validação
    dos access tokens JWT.

    A origem das chaves é definida através da configuração
    `JWT_KEY_PROVIDER`.

    Quando o provider é `local`, as chaves são carregadas
    a partir de arquivos locais.

    Quando o provider é `oci`, a chave privada é obtida através
    do OCI Secret Management utilizando Instance Principal.

    Returns:
        Instância configurada de `JwtService`.

    Raises:
        ValueError: Caso o provider de chaves JWT configurado
            não seja suportado.
    """

    if settings.jwt_key_provider == 'local':
        private_key = _load_local_private_key()
        public_key = _load_local_public_key()

    elif settings.jwt_key_provider == 'oci':
        private_key = _load_oci_private_key()
        public_key = _load_oci_public_key()

    else:
        raise ValueError(
            f'Unsupported JWT key provider: '
            f'{settings.jwt_key_provider}'
        )

    return JwtService(
        private_key=private_key,
        public_key=public_key,
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        access_token_expiration_minutes=(
            settings.jwt_access_token_expiration_minutes
        )
    )


def get_token_service() -> TokenService:
    """
    Fornece o serviço responsável pelas operações técnicas
    relacionadas à geração e ao hash de tokens aleatórios.

    Returns:
        Instância de `TokenService`.
    """

    return TokenService()


def _load_local_private_key() -> str:
    """
    Carrega a chave privada JWT a partir de um arquivo local.

    Returns:
        Conteúdo da chave privada em formato PEM.
    """

    return Path(
        settings.jwt_private_key_path
    ).read_text(
        encoding='utf-8'
    )


def _load_local_public_key() -> str:
    """
    Carrega a chave pública JWT a partir de um arquivo local.

    Returns:
        Conteúdo da chave pública em formato PEM.
    """

    return Path(
        settings.jwt_public_key_path
    ).read_text(
        encoding='utf-8'
    )


def _load_oci_public_key() -> str:
    """
    Carrega a chave pública JWT armazenada no OCI Vault.

    A autenticação utiliza o método configurado em OCI_AUTH_MODE,
    permitindo a execução em Compute, OKE e Container Instances.

    Returns:
        str: Conteúdo da chave pública em formato PEM.

    Raises:
        ValueError: Quando o identificador do Secret não está configurado
            ou o método de autenticação OCI não é suportado.
        oci.exceptions.ServiceError: Quando ocorre uma falha ao
            consultar o Secret no OCI Vault.
    """

    # Valida a configuração do Secret.
    if not settings.jwt_public_key_secret_id:
        raise ValueError(
            'JWT_PUBLIC_KEY_SECRET_ID não está configurado.'
        )

    # Obtém as credenciais conforme o método de autenticação OCI.
    config, signer = get_oci_credentials()

    # Cria o cliente responsável pela leitura dos Secrets.
    secrets_client = oci.secrets.SecretsClient(
        config=config,
        signer=signer
    )

    # Recupera a versão CURRENT do Secret no OCI Vault
    # que contém a chave pública utilizada para validar JWTs.
    response = secrets_client.get_secret_bundle(
        secret_id=settings.jwt_public_key_secret_id,
        stage='CURRENT'
    )

    # Obtém o conteúdo do Secret codificado em Base64.
    encoded_public_key = response.data.secret_bundle_content.content

    # Converte o conteúdo Base64 para o formato PEM.
    return base64.b64decode(encoded_public_key).decode('utf-8')


def _load_oci_private_key() -> str:
    """
    Carrega a chave privada JWT armazenada no OCI Vault.

    A autenticação utiliza o método configurado em OCI_AUTH_MODE,
    permitindo a execução em Compute, OKE e Container Instances.

    Returns:
        str: Conteúdo da chave privada em formato PEM.

    Raises:
        ValueError: Quando o método de autenticação OCI não é suportado
            ou o identificador do Secret não está configurado.
        oci.exceptions.ServiceError: Quando ocorre uma falha ao
            consultar o Secret no OCI Vault.
    """

    # Valida a configuração do Secret.
    if not settings.jwt_private_key_secret_id:
        raise ValueError(
            'JWT_PRIVATE_KEY_SECRET_ID não está configurado.'
        )

    # Obtém as credenciais conforme o método de autenticação OCI.
    config, signer = get_oci_credentials()

    # Cria o cliente responsável pela leitura dos Secrets.
    secrets_client = oci.secrets.SecretsClient(
        config=config,
        signer=signer
    )

    # Recupera a versão CURRENT do Secret no OCI Vault
    # que contém a chave privada utilizada para assinar JWTs.
    response = secrets_client.get_secret_bundle(
        secret_id=settings.jwt_private_key_secret_id,
        stage='CURRENT'
    )

    # Obtém o conteúdo do Secret codificado em Base64.
    encoded_private_key = response.data.secret_bundle_content.content

    # Converte o conteúdo Base64 para o formato PEM.
    return base64.b64decode(encoded_private_key).decode('utf-8')