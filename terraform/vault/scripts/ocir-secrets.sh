#!/usr/bin/env bash

# Cria ou atualiza o Secret persistente com as credenciais de acesso ao OCIR.

set -euo pipefail

ACTION="${1:-apply}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SECRET_NAME="ocipizza-ocir-credentials"

# Carrega as funções compartilhadas de integração com o OCI Vault.
source "$SCRIPT_DIR/vault.sh"

if [[ "$ACTION" == "destroy" ]]; then
  echo "Secret do OCIR é persistente; nenhuma ação será executada no destroy."
  exit 0
fi

if [[ "$ACTION" != "apply" ]]; then
  echo "Ação inválida: $ACTION. Use apply ou destroy." >&2
  exit 1
fi

: "${COMPARTMENT_ID:?Defina COMPARTMENT_ID.}"
: "${OCI_REGION:?Defina OCI_REGION.}"
: "${OCIR_USERNAME:?Defina OCIR_USERNAME.}"
: "${OCIR_AUTH_TOKEN:?Defina OCIR_AUTH_TOKEN.}"

validate_commands oci jq base64
display_secret_banner "Salvando as credenciais do OCIR no OCI Vault"
configure_oci_cli
resolve_vault_resources

# O jq lê as credenciais do ambiente para evitar expô-las como argumentos
# visíveis na lista de processos do sistema operacional.
credentials="$(jq -cn \
  '{username: env.OCIR_USERNAME, authToken: env.OCIR_AUTH_TOKEN}')"

upsert_secret \
  "$SECRET_NAME" \
  "Credenciais usadas pelas pipelines para criar o imagePullSecret do OCIR." \
  "$credentials"
