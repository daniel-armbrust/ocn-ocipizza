#
# dependencies/security.py
#

import base64
from pathlib import Path

import oci

from app.config.settings import settings
from app.services.jwt_service import JwtService
from app.services.token_service import TokenService


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


def _load_oci_private_key() -> str:
    """
    Carrega a chave privada JWT armazenada no OCI Secret Management.

    A autenticação com a OCI é realizada através de Instance Principal,
    evitando a necessidade de armazenar credenciais da OCI na aplicação.

    Returns:
        Conteúdo da chave privada em formato PEM.
    """

    # Obtém um signer baseado na identidade da própria instância OCI.
    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()

    # Cria o cliente responsável pela leitura dos secrets.
    secrets_client = oci.secrets.SecretsClient(config={}, signer=signer)

    # Recupera a versão CURRENT do secret que contém
    # a chave privada utilizada para assinatura dos JWTs.
    response = secrets_client.get_secret_bundle(
        secret_id=settings.jwt_private_key_secret_id,
        stage='CURRENT'
    )

    # O OCI Secret Management retorna o conteúdo do secret
    # codificado em Base64.
    encoded_private_key = (response.data.secret_bundle_content.content)

    # Converte o conteúdo Base64 novamente para o formato PEM.
    return base64.b64decode(encoded_private_key).decode('utf-8')


def _load_oci_public_key() -> str:
    """
    Carrega a chave pública JWT utilizada pelo user-service.

    A chave pública não é considerada um segredo e, por enquanto,
    permanece armazenada em um arquivo disponível para a aplicação.

    Returns:
        Conteúdo da chave pública em formato PEM.
    """

    return Path(
        settings.jwt_public_key_path
    ).read_text(
        encoding='utf-8'
    )


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