#!/usr/bin/env bash

# Cria ou atualiza os Secrets Kubernetes consumidos pelo user-service.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="user-service"

# Carrega as funções compartilhadas de integração com Vault e OKE.
source "$SCRIPT_DIR/lib/secrets.sh"

initialize_secrets_script
trap cleanup_temporary_directory EXIT

# O contrato abaixo fica pronto para o database-secrets.sh. Enquanto o MySQL
# não existir, a ausência desse Secret interrompe o deployment sem criar um
# recurso Kubernetes parcial.
database_url="$(read_vault_secret \
  "ocipizza-$ENVIRONMENT-$SERVICE_NAME-database-url")"
  
jwt_public_key="$(read_vault_secret \
  "ocipizza-$ENVIRONMENT-$SERVICE_NAME-jwt-public-key")"

apply_kubernetes_secret \
  "user-service-secrets" \
  "database-url" "$database_url"

apply_kubernetes_secret \
  "user-service-jwt-public-key" \
  "jwt_public_key.pem" "$jwt_public_key"
