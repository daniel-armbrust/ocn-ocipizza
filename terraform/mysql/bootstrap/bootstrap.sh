#!/usr/bin/env bash

# Cria o usuário de privilégio mínimo no primary e configura, de maneira
# idempotente, o canal de replicação assíncrona no secondary.

set -euo pipefail

CHANNEL_DISPLAY_NAME="mysql-gru-to-vcp"
CHANNEL_NAME="ocipizza_gru_to_vcp"
MYSQL_PRIMARY_REGION="${MYSQL_PRIMARY_REGION:-sa-saopaulo-1}"
MYSQL_SECONDARY_REGION="${MYSQL_SECONDARY_REGION:-sa-vinhedo-1}"
MYSQL_PRIMARY_HOST="${MYSQL_PRIMARY_HOST:-mysql-write.ocipizza.internal}"
MYSQL_PRIMARY_PORT="${MYSQL_PRIMARY_PORT:-3306}"
PYTHON_BIN="${PYTHON_BIN:-python3.11}"
TEMPORARY_DIRECTORY=""
OCI_OPTIONS=(--auth resource_principal)

# Remove os arquivos temporários que contêm credenciais ou requests da OCI.
cleanup_temporary_directory() {
  if [[ -n "$TEMPORARY_DIRECTORY" && -d "$TEMPORARY_DIRECTORY" ]]; then
    rm -f -- "$TEMPORARY_DIRECTORY"/*.json
    rmdir -- "$TEMPORARY_DIRECTORY"
  fi
}

# Exibe uma etapa do bootstrap em um bloco destacado no terminal.
display_step() {
  local message="$1"
  local border

  printf -v border '%*s' "$(( ${#message} + 4 ))" ''
  border="${border// /#}"
  printf '\n%s\n# %s #\n%s\n\n' "$border" "$message" "$border"
}

# Centraliza a autenticação por Resource Principal nas chamadas da OCI CLI.
oci_cli() {
  local region="$1"

  shift
  oci "${OCI_OPTIONS[@]}" --region "$region" "$@"
}

# Recupera a versão CURRENT de um Secret e salva o JSON em arquivo protegido.
read_credentials_secret() {
  local secret_id="$1"
  local output_file="$2"
  local encoded_content

  encoded_content="$(oci_cli "$MYSQL_PRIMARY_REGION" \
    secrets secret-bundle get \
    --secret-id "$secret_id" \
    --stage CURRENT \
    --query 'data."secret-bundle-content".content' \
    --raw-output)"

  printf '%s' "$encoded_content" | base64 --decode >"$output_file"
  chmod 600 "$output_file"

  if ! jq -e '
    (.username | type == "string" and length > 0)
    and (.password | type == "string" and length >= 8 and length <= 32)
  ' >/dev/null <"$output_file"; then
    echo "O Secret $secret_id não contém credenciais válidas." >&2
    return 1
  fi
}

# Cria ou atualiza o usuário usado exclusivamente pelo canal de replicação.
configure_replication_user() {
  "$PYTHON_BIN" - "$TEMPORARY_DIRECTORY/admin.json" \
    "$TEMPORARY_DIRECTORY/replication.json" <<'PYTHON'
import json
import os
import re
import sys

import pymysql


def read_credentials(path: str) -> dict[str, str]:
    """Lê um arquivo temporário de credenciais validado pelo shell."""
    with open(path, encoding='utf-8') as credentials_file:
        return json.load(credentials_file)


admin_credentials = read_credentials(sys.argv[1])
replication_credentials = read_credentials(sys.argv[2])
replication_username = replication_credentials['username']

if not re.fullmatch(r'[a-z][a-z0-9_]{0,31}', replication_username):
    raise ValueError('O username de replicação contém caracteres inválidos.')

connection = pymysql.connect(
    host=os.environ['MYSQL_PRIMARY_HOST'],
    port=int(os.environ['MYSQL_PRIMARY_PORT']),
    user=admin_credentials['username'],
    password=admin_credentials['password'],
    charset='utf8mb4',
    connect_timeout=15,
    # O certificado SYSTEM do MySQL HeatWave não possui uma CA disponível no
    # trust store do Managed Build. A conexão permanece criptografada, em
    # alinhamento com o modo REQUIRED usado pelo canal de replicação.
    ssl_verify_cert=False,
)

try:
    with connection.cursor() as cursor:
        cursor.execute(
            f"CREATE USER IF NOT EXISTS '{replication_username}'@'%' "
            'IDENTIFIED BY %s REQUIRE SSL',
            (replication_credentials['password'],),
        )

        cursor.execute(
            f"ALTER USER '{replication_username}'@'%' "
            'IDENTIFIED BY %s REQUIRE SSL',
            (replication_credentials['password'],),
        )

        cursor.execute(
            'GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* '
            f"TO '{replication_username}'@'%'"
        )

    connection.commit()
finally:
    connection.close()

print('Usuário exclusivo de replicação configurado no primary.')
PYTHON
}

# Localiza o canal ainda existente que aponta para o DB System secondary.
resolve_existing_channel_id() {
  local channels_json

  channels_json="$(oci_cli "$MYSQL_SECONDARY_REGION" mysql channel list \
    --compartment-id "$COMPARTMENT_ID" \
    --all)"

  jq -r \
    --arg display_name "$CHANNEL_DISPLAY_NAME" \
    --arg target_id "$MYSQL_SECONDARY_DB_SYSTEM_ID" '
      (if (.data | type) == "array"
       then .data
       else (.data.items // [])
       end)
      | map(select(
          ."display-name" == $display_name
          and .target."db-system-id" == $target_id
          and .state != "DELETED"
        ))
      | sort_by(."time-created")
      | last.id // empty
    ' <<<"$channels_json"
}

# Cria o canal sem expor a senha de replicação na lista de processos.
create_replication_channel() {
  local request_file="$TEMPORARY_DIRECTORY/create-channel.json"
  local replication_username
  local replication_password

  replication_username="$(jq -er '.username' "$TEMPORARY_DIRECTORY/replication.json")"
  replication_password="$(jq -er '.password' "$TEMPORARY_DIRECTORY/replication.json")"

  jq -cn \
    --arg compartment_id "$COMPARTMENT_ID" \
    --arg display_name "$CHANNEL_DISPLAY_NAME" \
    --arg source_hostname "$MYSQL_PRIMARY_HOST" \
    --arg source_username "$replication_username" \
    --arg source_password "$replication_password" \
    --arg target_db_system_id "$MYSQL_SECONDARY_DB_SYSTEM_ID" \
    --arg target_channel_name "$CHANNEL_NAME" '
      {
        compartmentId: $compartment_id,
        displayName: $display_name,
        description: "Replicação assíncrona do MySQL primary de GRU para VCP.",
        isEnabled: true,
        sourceHostname: $source_hostname,
        sourcePort: 3306,
        sourceUsername: $source_username,
        sourcePassword: $source_password,
        sourceSslMode: "REQUIRED",
        sourceAnonymousTransactionsHandling: {
          policy: "ASSIGN_TARGET_UUID"
        },
        targetDbSystemId: $target_db_system_id,
        targetChannelName: $target_channel_name,
        targetTablesWithoutPrimaryKeyHandling: "ALLOW"
      }
    ' >"$request_file"
  chmod 600 "$request_file"

  oci_cli "$MYSQL_SECONDARY_REGION" mysql channel create-from-mysql \
    --from-json "file://$request_file" \
    --wait-for-state SUCCEEDED \
    --max-wait-seconds 1200 >/dev/null

  resolve_existing_channel_id
}

# Reativa um canal existente que esteja apenas desabilitado.
ensure_channel_enabled() {
  local channel_id="$1"
  local channel_state

  channel_state="$(oci_cli "$MYSQL_SECONDARY_REGION" mysql channel get \
    --channel-id "$channel_id" \
    --query 'data.state' \
    --raw-output)"

  case "$channel_state" in
    ACTIVE | CREATING | UPDATING)
      ;;

    INACTIVE)
      echo "Reativando o canal de replicação existente..."
      oci_cli "$MYSQL_SECONDARY_REGION" mysql channel resume \
        --channel-id "$channel_id" \
        --wait-for-state SUCCEEDED \
        --max-wait-seconds 1200 >/dev/null
      ;;

    *)
      echo "O canal existente está no estado $channel_state e requer intervenção." >&2
      return 1
      ;;

  esac
}

# Valida os pré-requisitos antes de acessar Secrets ou bancos.
validate_inputs() {
  local command

  for command in oci jq base64 "$PYTHON_BIN"; do
    if ! command -v "$command" >/dev/null 2>&1; then
      echo "O comando $command é obrigatório." >&2
      return 1
    fi
  done

  [[ "${OCI_AUTH_MODE:-}" == "resource_principal" ]] || {
    echo "OCI_AUTH_MODE deve ser resource_principal." >&2
    return 1
  }

  : "${COMPARTMENT_ID:?Defina COMPARTMENT_ID.}"
  : "${MYSQL_PRIMARY_DB_SYSTEM_ID:?Defina MYSQL_PRIMARY_DB_SYSTEM_ID.}"
  : "${MYSQL_SECONDARY_DB_SYSTEM_ID:?Defina MYSQL_SECONDARY_DB_SYSTEM_ID.}"
  : "${MYSQL_ADMIN_CREDENTIALS_SECRET_ID:?Defina MYSQL_ADMIN_CREDENTIALS_SECRET_ID.}"
  : "${MYSQL_REPLICATION_CREDENTIALS_SECRET_ID:?Defina MYSQL_REPLICATION_CREDENTIALS_SECRET_ID.}"

  export MYSQL_PRIMARY_HOST MYSQL_PRIMARY_PORT
}

# Orquestra o bootstrap idempotente da replicação cross-region.
main() {
  local channel_id

  validate_inputs
  TEMPORARY_DIRECTORY="$(mktemp -d "${OCI_WORKSPACE_DIR:-.}/mysql-bootstrap.XXXXXX")"
  chmod 700 "$TEMPORARY_DIRECTORY"
  trap cleanup_temporary_directory EXIT

  display_step 'Lendo credenciais MySQL no OCI Vault'

  read_credentials_secret \
    "$MYSQL_ADMIN_CREDENTIALS_SECRET_ID" \
    "$TEMPORARY_DIRECTORY/admin.json"
  
  read_credentials_secret \
    "$MYSQL_REPLICATION_CREDENTIALS_SECRET_ID" \
    "$TEMPORARY_DIRECTORY/replication.json"

  display_step 'Configurando o usuário de replicação no primary'
  configure_replication_user

  display_step 'Configurando o canal de replicação no secondary'
  channel_id="$(resolve_existing_channel_id)"

  if [[ -z "$channel_id" ]]; then
    channel_id="$(create_replication_channel)"
  else
    echo "Canal de replicação já existe; mantendo o recurso atual."
    ensure_channel_enabled "$channel_id"
  fi

  if [[ -z "$channel_id" ]]; then
    echo "Não foi possível resolver o OCID do canal de replicação." >&2
    return 1
  fi

  display_step 'Validando a replicação MySQL'
  MYSQL_CHANNEL_ID="$channel_id" \
    MYSQL_SECONDARY_REGION="$MYSQL_SECONDARY_REGION" \
    OCI_AUTH_MODE="$OCI_AUTH_MODE" \
    bash "$(dirname -- "${BASH_SOURCE[0]}")/validate-replication.sh"
}

main "$@"
