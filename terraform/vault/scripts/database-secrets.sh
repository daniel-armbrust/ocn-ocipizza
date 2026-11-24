#!/usr/bin/env bash

# Gera credenciais persistentes do MySQL e armazena cada finalidade em um
# Secret independente no OCI Vault.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ADMIN_SECRET_NAME="ocipizza-mysql-admin-credentials"
REPLICATION_SECRET_NAME="ocipizza-mysql-replication-credentials"
USER_SERVICE_SECRET_NAME="ocipizza-user-service-database-credentials"
ADMIN_USERNAME="ocipizza_admin"
REPLICATION_USERNAME="ocipizza_replicator"
USER_SERVICE_USERNAME="user_service"

# Carrega as funções compartilhadas de integração com o OCI Vault.
source "$SCRIPT_DIR/vault.sh"

# Gera 112 bits aleatórios e acrescenta caracteres de todas as classes
# exigidas pelo MySQL, mantendo o resultado com exatamente 32 caracteres.
generate_mysql_password() {
  printf 'Aa%s1!' "$(openssl rand -hex 14)"
}

# Recupera credenciais existentes ou cria um documento JSON persistente.
ensure_database_credentials() {
  local secret_name="$1"
  local username="$2"
  local description="$3"
  local secret_id
  local password
  local credentials

  secret_id="$(resolve_secret_id "$secret_name")"

  if [[ -z "$secret_id" ]]; then
    password="$(generate_mysql_password)"

    credentials="$(jq -cn \
      --arg username "$username" \
      --arg password "$password" \
      '{username: $username, password: $password}')"

    secret_id="$(create_secret "$secret_name" "$description" "$credentials")"
  fi

  credentials="$(read_secret_content "$secret_id")"

  if ! jq -e '
    (.username | type == "string" and length > 0)
    and (.password | type == "string" and length >= 8 and length <= 32)
  ' >/dev/null <<<"$credentials"; then
    echo "O Secret $secret_name não contém credenciais MySQL válidas." >&2
    return 1
  fi

  printf '%s' "$credentials"
}

# Executa a geração idempotente e retorna somente o JSON esperado pelo
# external data source do Terraform em stdout.
main() {
  local query
  local admin_credentials
  local replication_credentials
  local user_service_credentials

  query="$(cat)"
  COMPARTMENT_ID="$(jq -er '.compartment_id' <<<"$query")"
  OCI_REGION="$(jq -er '.region' <<<"$query")"

  display_secret_banner "Gerando e salvando as credenciais MySQL no OCI Vault"
  validate_commands oci jq base64 openssl
  configure_oci_cli
  resolve_vault_resources

  admin_credentials="$(ensure_database_credentials \
    "$ADMIN_SECRET_NAME" \
    "$ADMIN_USERNAME" \
    "Credenciais administrativas do MySQL HeatWave da OCI Pizza.")"

  replication_credentials="$(ensure_database_credentials \
    "$REPLICATION_SECRET_NAME" \
    "$REPLICATION_USERNAME" \
    "Credenciais do canal de replicação cross-region do MySQL HeatWave.")"

  user_service_credentials="$(ensure_database_credentials \
    "$USER_SERVICE_SECRET_NAME" \
    "$USER_SERVICE_USERNAME" \
    "Credenciais do banco de dados do user-service.")"

  # Valida o documento antes de concluir, sem expor suas credenciais no state.
  jq -e '.username and .password' >/dev/null <<<"$user_service_credentials"

  jq -cn \
    --arg admin_username "$(jq -er '.username' <<<"$admin_credentials")" \
    --arg admin_password "$(jq -er '.password' <<<"$admin_credentials")" \
    --arg replication_username "$(jq -er '.username' <<<"$replication_credentials")" \
    --arg replication_password "$(jq -er '.password' <<<"$replication_credentials")" \
    '{admin_username: $admin_username, admin_password: $admin_password,
      replication_username: $replication_username,
      replication_password: $replication_password}'
}

main "$@"
