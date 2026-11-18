#!/usr/bin/env bash

# Exclui a Security List redis-security-list criada automaticamente pelo OCI
# Cache após a criação do cluster.
# TODO: remover este workaround quando o OCI Cache deixar de criar uma
# Security List adicional.

set -euo pipefail

readonly SECURITY_LIST_NAME="redis-security-list"
OCI_OPTIONS=()

# Centraliza as opções comuns para todas as chamadas da OCI CLI.
oci_cli() {
  oci "${OCI_OPTIONS[@]}" "$@"
}

: "${COMPARTMENT_ID:?Defina COMPARTMENT_ID.}"
: "${OCI_REGION:?Defina OCI_REGION.}"
: "${SUBNET_ID:?Defina SUBNET_ID.}"
: "${VCN_ID:?Defina VCN_ID.}"

for command in oci jq; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "O comando $command é obrigatório." >&2
    exit 1
  fi
done

OCI_OPTIONS=(--region "$OCI_REGION")

if [[ -n "${OCI_CONFIG_FILE_PROFILE:-}" ]]; then
  OCI_OPTIONS+=(--profile "$OCI_CONFIG_FILE_PROFILE")
fi

if [[ -n "${OCI_CONFIG_FILE:-}" ]]; then
  OCI_OPTIONS+=(--config-file "$OCI_CONFIG_FILE")
fi

security_list_id="$(oci_cli network security-list list \
  --compartment-id "$COMPARTMENT_ID" \
  --vcn-id "$VCN_ID" \
  --display-name "$SECURITY_LIST_NAME" \
  --all \
  --query 'data[0].id' \
  --raw-output)"

if [[ -z "$security_list_id" || "$security_list_id" == "null" || "$security_list_id" == "None" ]]; then
  echo "$SECURITY_LIST_NAME não foi encontrada; nenhuma exclusão necessária."
  exit 0
fi

echo "Preparando exclusão de $SECURITY_LIST_NAME ($security_list_id)..."

security_list_ids="$(oci_cli network subnet get \
  --subnet-id "$SUBNET_ID" \
  --query 'data."security-list-ids"' \
  --output json)"

updated_security_list_ids="$(jq -c \
  --arg security_list_id "$security_list_id" \
  'map(select(. != $security_list_id))' \
  <<<"$security_list_ids")"

if [[ "$updated_security_list_ids" == "[]" ]]; then
  echo "A subnet $SUBNET_ID ficaria sem Security List; exclusão interrompida." >&2
  exit 1
fi

if jq -e --arg security_list_id "$security_list_id" \
  'index($security_list_id) != null' <<<"$security_list_ids" >/dev/null; then
  echo "Removendo $SECURITY_LIST_NAME da subnet $SUBNET_ID..."

  oci_cli network subnet update \
    --subnet-id "$SUBNET_ID" \
    --security-list-ids "$updated_security_list_ids" \
    --force \
    --wait-for-state AVAILABLE >/dev/null
fi

oci_cli network security-list delete \
  --security-list-id "$security_list_id" \
  --force \
  --wait-for-state TERMINATED >/dev/null

echo "$SECURITY_LIST_NAME excluída com sucesso."

exit 0
