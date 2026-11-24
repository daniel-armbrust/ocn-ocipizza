#!/usr/bin/env bash

# Aguarda o canal de replicação ficar ativo e falha quando a OCI informa um
# estado terminal ou que exige intervenção operacional.

set -euo pipefail

MAX_ATTEMPTS=60
RETRY_INTERVAL_SECONDS=10
MYSQL_SECONDARY_REGION="${MYSQL_SECONDARY_REGION:-sa-vinhedo-1}"

# Consulta o canal até que ele fique ativo ou alcance um estado de falha.
validate_channel() {
  local attempt
  local channel_json
  local channel_state
  local lifecycle_details

  for ((attempt = 1; attempt <= MAX_ATTEMPTS; attempt++)); do
    channel_json="$(oci --auth resource_principal \
      --region "$MYSQL_SECONDARY_REGION" \
      mysql channel get \
      --channel-id "$MYSQL_CHANNEL_ID")"

    channel_state="$(jq -r '.data."lifecycle-state" // empty' <<<"$channel_json")"

    lifecycle_details="$(jq -r '.data."lifecycle-details" // empty' <<<"$channel_json")"

    case "$channel_state" in
      ACTIVE)
        echo "Canal de replicação ativo: $MYSQL_CHANNEL_ID"
        return 0
        ;;

      CREATING | UPDATING)
        echo "Aguardando o canal ficar ACTIVE: $channel_state ($attempt/$MAX_ATTEMPTS)..."
        sleep "$RETRY_INTERVAL_SECONDS"
        ;;

      NEEDS_ATTENTION)
        if [[ "$lifecycle_details" == *"connection may be in progress"* ]]; then
          echo "A conexão do canal ainda está em andamento ($attempt/$MAX_ATTEMPTS)..."
          sleep "$RETRY_INTERVAL_SECONDS"
          continue
        fi

        echo "Canal no estado $channel_state: ${lifecycle_details:-detalhes não informados pela OCI}." >&2
        return 1
        ;;

      FAILED | DELETING | DELETED | INACTIVE)
        echo "Canal no estado $channel_state: ${lifecycle_details:-detalhes não informados pela OCI}." >&2
        return 1
        ;;

      *)
        echo "Estado inesperado do canal: ${channel_state:-vazio}." >&2
        return 1
        ;;

    esac
  done

  echo "Tempo limite excedido ao aguardar o canal ficar ACTIVE." >&2
  return 1
}

# Valida as entradas e inicia o acompanhamento do canal.
main() {
  command -v oci >/dev/null 2>&1 || {
    echo "O comando oci é obrigatório." >&2
    return 1
  }

  command -v jq >/dev/null 2>&1 || {
    echo "O comando jq é obrigatório." >&2
    return 1
  }

  [[ "${OCI_AUTH_MODE:-}" == "resource_principal" ]] || {
    echo "OCI_AUTH_MODE deve ser resource_principal." >&2
    return 1
  }
  : "${MYSQL_CHANNEL_ID:?Defina MYSQL_CHANNEL_ID.}"

  validate_channel
}

main "$@"
