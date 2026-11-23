#!/usr/bin/env bash

# Cria ou atualiza o Secret persistente que armazena o PAT do GitHub.

set -euo pipefail

ACTION="${1:-apply}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SECRET_NAME="ocipizza-github-pat"

# Carrega as funções compartilhadas de integração com o OCI Vault.
source "$SCRIPT_DIR/vault.sh"

if [[ "$ACTION" == "destroy" ]]; then
  echo "Secret do GitHub é persistente; nenhuma ação será executada no destroy."
  exit 0
fi

if [[ "$ACTION" != "apply" ]]; then
  echo "Ação inválida: $ACTION. Use apply ou destroy." >&2
  exit 1
fi

: "${COMPARTMENT_ID:?Defina COMPARTMENT_ID.}"
: "${OCI_REGION:?Defina OCI_REGION.}"
: "${GITHUB_PAT:?Defina GITHUB_PAT.}"

display_secret_banner "Salvando o PAT do GitHub no OCI Vault"
validate_commands oci jq base64
configure_oci_cli
resolve_vault_resources

upsert_secret \
  "$SECRET_NAME" \
  "PAT do GitHub usado pelo OCI DevOps do OCI Pizza." \
  "$GITHUB_PAT"