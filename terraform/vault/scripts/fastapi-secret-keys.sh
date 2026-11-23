#!/usr/bin/env bash

# Gera e armazena no OCI Vault as chaves de sessão e CSRF de um serviço.

set -euo pipefail

ACTION="${1:-apply}"
ENVIRONMENT="${2:-}"
SERVICE_NAME="${3:-}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

# Carrega as funções compartilhadas de integração com o OCI Vault.
source "$SCRIPT_DIR/vault.sh"

# Gera uma chave aleatória de 512 bits representada em hexadecimal.
generate_fastapi_key() {
  openssl rand -hex 64
}

if [[ "$ACTION" == "destroy" ]]; then
  echo "Secrets FastAPI são persistentes; nenhuma ação será executada no destroy."
  exit 0
fi

if [[ "$ACTION" != "apply" ]]; then
  echo "Ação inválida: $ACTION. Use apply ou destroy." >&2
  exit 1
fi

: "${COMPARTMENT_ID:?Defina COMPARTMENT_ID.}"
: "${OCI_REGION:?Defina OCI_REGION.}"

if [[ ! "$ENVIRONMENT" =~ ^(homol|prod)$ ]]; then
  echo "Ambiente inválido: use homol ou prod." >&2
  exit 1
fi

if [[ ! "$SERVICE_NAME" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "Nome de serviço inválido: $SERVICE_NAME." >&2
  exit 1
fi

display_secret_banner "Gerando e salvando os secrets FastAPI de $SERVICE_NAME/$ENVIRONMENT no OCI Vault"
validate_commands oci jq base64 openssl
configure_oci_cli
resolve_vault_resources

session_secret_name="ocipizza-$ENVIRONMENT-$SERVICE_NAME-session-secret-key"
csrf_secret_name="ocipizza-$ENVIRONMENT-$SERVICE_NAME-csrf-secret-key"

create_generated_secret_if_absent \
  "$session_secret_name" \
  "Chave de sessão do $SERVICE_NAME no ambiente $ENVIRONMENT." \
  generate_fastapi_key >/dev/null

create_generated_secret_if_absent \
  "$csrf_secret_name" \
  "Chave de proteção CSRF do $SERVICE_NAME no ambiente $ENVIRONMENT." \
  generate_fastapi_key >/dev/null

echo "Secrets FastAPI de $SERVICE_NAME/$ENVIRONMENT disponíveis no OCI Vault."