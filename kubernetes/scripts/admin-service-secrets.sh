#!/usr/bin/env bash

# Cria ou atualiza os Secrets Kubernetes consumidos pelo admin-service.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="admin-service"
REDIS_DATABASE="1"

# Carrega as funções compartilhadas de integração com Vault e OKE.
source "$SCRIPT_DIR/lib/secrets.sh"

: "${REDIS_HOST:?Defina REDIS_HOST.}"
: "${REDIS_PORT:=6379}"

validate_redis_connection
initialize_secrets_script
trap cleanup_temporary_directory EXIT

redis_credentials="$(read_vault_secret \
  "ocipizza-$ENVIRONMENT-$SERVICE_NAME-redis-credentials")"

session_secret_key="$(read_vault_secret \
  "ocipizza-$ENVIRONMENT-$SERVICE_NAME-session-secret-key")"
  
csrf_secret_key="$(read_vault_secret \
  "ocipizza-$ENVIRONMENT-$SERVICE_NAME-csrf-secret-key")"

redis_username="$(jq -er '.username' <<<"$redis_credentials")"
redis_password="$(jq -er '.password' <<<"$redis_credentials")"
redis_endpoint="redis://${redis_username}:${redis_password}@${REDIS_HOST}:${REDIS_PORT}/${REDIS_DATABASE}"

apply_kubernetes_secret \
  "admin-service-secrets" \
  "redis-endpoint" "$redis_endpoint" \
  "session-secret-key" "$session_secret_key" \
  "csrf-secret-key" "$csrf_secret_key"
