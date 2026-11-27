#!/usr/bin/env bash

# Cria ou atualiza os Secrets Kubernetes consumidos pelo user-service.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="user-service"

# Carrega as funções compartilhadas de integração com Vault e OKE.
source "$SCRIPT_DIR/lib/secrets.sh"

initialize_secrets_script
trap cleanup_temporary_directory EXIT

# As credenciais são compartilhadas pelos endpoints de escrita e leitura. Os
# hostnames privados selecionam o primary e o banco regional, respectivamente.
database_credentials="$(read_vault_secret \
  "ocipizza-$SERVICE_NAME-database-credentials")"

if ! jq -e '
  (.username | type == "string" and length > 0)
  and (.password | type == "string" and length > 0)
' >/dev/null <<<"$database_credentials"; then
  echo 'O Secret de credenciais do user-service possui formato inválido.' >&2
  exit 1
fi

database_username="$(jq -er '.username | @uri' <<<"$database_credentials")"
database_password="$(jq -er '.password | @uri' <<<"$database_credentials")"
database_write_url="mysql+pymysql://${database_username}:${database_password}@mysql-write.ocipizza.internal:3306/users?ssl_verify_cert=false"
database_read_url="mysql+pymysql://${database_username}:${database_password}@mysql-read.ocipizza.internal:3306/users?ssl_verify_cert=false"

jwt_public_key="$(read_vault_secret \
  "ocipizza-$ENVIRONMENT-$SERVICE_NAME-jwt-public-key")"

apply_kubernetes_secret \
  "user-service-secrets" \
  "database-write-url" "$database_write_url" \
  "database-read-url" "$database_read_url"

apply_kubernetes_secret \
  "user-service-jwt-public-key" \
  "jwt_public_key.pem" "$jwt_public_key"
