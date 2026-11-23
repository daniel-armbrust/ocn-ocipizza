#!/usr/bin/env bash

# Gera e armazena no OCI Vault o par de chaves RSA usado pelos tokens JWT.

set -euo pipefail

ACTION="${1:-apply}"
ENVIRONMENT="${2:-}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
TEMPORARY_DIRECTORY=""

# Carrega as funções compartilhadas de integração com o OCI Vault.
source "$SCRIPT_DIR/vault.sh"

# Remove os arquivos temporários que contêm o par de chaves JWT.
cleanup_temporary_directory() {
  if [[ -n "$TEMPORARY_DIRECTORY" && -d "$TEMPORARY_DIRECTORY" ]]; then
    rm -f -- \
      "$TEMPORARY_DIRECTORY/private.pem" \
      "$TEMPORARY_DIRECTORY/public.pem" \
      "$TEMPORARY_DIRECTORY/public.der" \
      "$TEMPORARY_DIRECTORY/stored-public.pem" \
      "$TEMPORARY_DIRECTORY/stored-public.der"
    rmdir -- "$TEMPORARY_DIRECTORY"
  fi
}

# Gera uma chave privada RSA de 3072 bits e deriva sua chave pública.
generate_jwt_key_pair() {
  openssl genpkey \
    -algorithm RSA \
    -pkeyopt rsa_keygen_bits:3072 \
    -out "$TEMPORARY_DIRECTORY/private.pem" 2>/dev/null

  openssl pkey \
    -in "$TEMPORARY_DIRECTORY/private.pem" \
    -pubout \
    -out "$TEMPORARY_DIRECTORY/public.pem"
}

# Recupera a chave privada existente e deriva novamente sua chave pública.
restore_public_key_from_private_secret() {
  local private_secret_id="$1"

  read_secret_content "$private_secret_id" >"$TEMPORARY_DIRECTORY/private.pem"
 
  openssl pkey \
    -in "$TEMPORARY_DIRECTORY/private.pem" \
    -pubout \
    -out "$TEMPORARY_DIRECTORY/public.pem"
}

# Confirma que as chaves privada e pública existentes pertencem ao mesmo par.
validate_existing_jwt_key_pair() {
  local private_secret_id="$1"
  local public_secret_id="$2"

  read_secret_content "$private_secret_id" >"$TEMPORARY_DIRECTORY/private.pem"
  read_secret_content "$public_secret_id" >"$TEMPORARY_DIRECTORY/stored-public.pem"
  
  openssl pkey \
    -in "$TEMPORARY_DIRECTORY/private.pem" \
    -pubout \
    -outform DER \
    -out "$TEMPORARY_DIRECTORY/public.der"
  
  openssl pkey \
    -pubin \
    -in "$TEMPORARY_DIRECTORY/stored-public.pem" \
    -outform DER \
    -out "$TEMPORARY_DIRECTORY/stored-public.der"

  if ! cmp -s \
    "$TEMPORARY_DIRECTORY/public.der" \
    "$TEMPORARY_DIRECTORY/stored-public.der"; then
    echo "As chaves JWT existentes de $ENVIRONMENT não pertencem ao mesmo par." >&2
    return 1
  fi
}

if [[ "$ACTION" == "destroy" ]]; then
  echo "Secrets JWT são persistentes; nenhuma ação será executada no destroy."
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

display_secret_banner "Gerando e salvando as chaves JWT de $ENVIRONMENT no OCI Vault"
validate_commands oci jq base64 openssl
configure_oci_cli
resolve_vault_resources

private_secret_name="ocipizza-$ENVIRONMENT-user-service-jwt-private-key"
public_secret_name="ocipizza-$ENVIRONMENT-user-service-jwt-public-key"
private_secret_id="$(resolve_secret_id "$private_secret_name")"
public_secret_id="$(resolve_secret_id "$public_secret_name")"

if [[ -n "$private_secret_id" && -n "$public_secret_id" ]]; then
  validate_commands cmp
  TEMPORARY_DIRECTORY="$(mktemp -d)"
  trap cleanup_temporary_directory EXIT
  chmod 700 "$TEMPORARY_DIRECTORY"
  validate_existing_jwt_key_pair "$private_secret_id" "$public_secret_id"
  echo "Par de chaves JWT de $ENVIRONMENT já existe; mantendo o conteúdo atual."
  exit 0
fi

if [[ -z "$private_secret_id" && -n "$public_secret_id" ]]; then
  echo "A chave pública existe sem a chave privada correspondente; corrija o Secret antes de continuar." >&2
  exit 1
fi

TEMPORARY_DIRECTORY="$(mktemp -d)"
trap cleanup_temporary_directory EXIT
chmod 700 "$TEMPORARY_DIRECTORY"

if [[ -n "$private_secret_id" ]]; then
  restore_public_key_from_private_secret "$private_secret_id"
else
  generate_jwt_key_pair

  create_secret_if_absent \
    "$private_secret_name" \
    "Chave privada JWT do user-service no ambiente $ENVIRONMENT." \
    "$(<"$TEMPORARY_DIRECTORY/private.pem")" >/dev/null
fi

create_secret_if_absent \
  "$public_secret_name" \
  "Chave pública JWT do user-service no ambiente $ENVIRONMENT." \
  "$(<"$TEMPORARY_DIRECTORY/public.pem")" >/dev/null

echo "Par de chaves JWT de $ENVIRONMENT disponível no OCI Vault."