#
# dependencies/oci_credentials.py
#

import oci

from app.config.settings import settings


def get_oci_credentials() -> tuple[dict, object | None]:
    """
    Obtém as credenciais conforme o método de autenticação OCI.

    Returns:
        tuple: Configuração OCI e signer, quando aplicável.

    Raises:
        ValueError: Quando o método de autenticação não é suportado.
        oci.exceptions.ConfigFileNotFound: Quando o arquivo de
            configuração OCI não é encontrado.
        oci.exceptions.InvalidConfig: Quando a configuração OCI é inválida.
    """

    # Autenticação por arquivo de configuração local.
    if settings.oci_auth_mode == 'config_file':
        config = oci.config.from_file(profile_name=settings.oci_config_profile)
        return config, None

    # Autenticação pela identidade da instância Compute.
    if settings.oci_auth_mode == 'instance_principal':
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()

    # Autenticação pela identidade do workload no OKE.
    elif settings.oci_auth_mode == 'workload_identity':
        signer = oci.auth.signers.get_oke_workload_identity_resource_principal_signer()

    # Autenticação pela identidade do recurso OCI.
    elif settings.oci_auth_mode == 'resource_principal':
        signer = oci.auth.signers.get_resource_principals_signer()
    
    else:
        raise ValueError(
            f'Método de autenticação OCI não suportado: {settings.oci_auth_mode}'
        )

    return {}, signer