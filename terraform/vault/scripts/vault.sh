#!/usr/bin/env bash

# Cria o Vault e a chave persistentes do OCI Pizza. Quando carregado por outro
# script, também fornece as funções compartilhadas de gerenciamento de secrets.

VAULT_NAME="ocipizza-vault"
KEY_NAME="ocipizza-vault-key"
OCI_OPTIONS=()
VAULT_ID=""
KEY_ID=""

# Exibe uma mensagem delimitada por caracteres # para destacar a operação.
display_secret_banner() {
  local message="$1"
  local border

  printf -v border '%*s' "$(( ${#message} + 4 ))" ''
  border="${border// /#}"

  printf '\n%s\n# %s #\n%s\n\n' "$border" "$message" "$border" >&2
}

# Centraliza as opções comuns para todas as chamadas da OCI CLI.
oci_cli() {
  oci "${OCI_OPTIONS[@]}" "$@"
}

# Valida a lista de ferramentas exigidas pelo script chamador.
validate_commands() {
  local command

  for command in "$@"; do
    if ! command -v "$command" >/dev/null 2>&1; then
      echo "O comando $command é obrigatório." >&2
      return 1
    fi
  done
}

# Configura a OCI CLI com a região e a configuração local opcionais.
configure_oci_cli() {
  OCI_OPTIONS=(--region "$OCI_REGION")

  if [[ -n "${OCI_CONFIG_FILE_PROFILE:-}" ]]; then
    OCI_OPTIONS+=(--profile "$OCI_CONFIG_FILE_PROFILE")
  fi

  if [[ -n "${OCI_CONFIG_FILE:-}" ]]; then
    OCI_OPTIONS+=(--config-file "$OCI_CONFIG_FILE")
  fi
}

# Localiza o Vault persistente e sua chave de criptografia habilitada.
resolve_vault_resources() {
  local vaults_json
  local vault_json
  local management_endpoint
  local keys_json

  vaults_json="$(oci_cli kms management vault list \
    --compartment-id "$COMPARTMENT_ID" \
    --all)"

  VAULT_ID="$(jq -r --arg name "$VAULT_NAME" '
    [.data[] | select(."display-name" == $name and ."lifecycle-state" == "ACTIVE")]
    | sort_by(."time-created") | reverse | .[0].id // empty
  ' <<<"$vaults_json")"

  if [[ -z "$VAULT_ID" ]]; then
    echo "Vault ativo $VAULT_NAME não encontrado." >&2
    return 1
  fi

  vault_json="$(oci_cli kms management vault get --vault-id "$VAULT_ID")"
  management_endpoint="$(jq -r '.data."management-endpoint"' <<<"$vault_json")"

  keys_json="$(oci_cli kms management key list \
    --endpoint "$management_endpoint" \
    --compartment-id "$COMPARTMENT_ID" \
    --all)"

  KEY_ID="$(jq -r --arg name "$KEY_NAME" '
    [.data[] | select(."display-name" == $name and ."lifecycle-state" == "ENABLED")]
    | sort_by(."time-created") | reverse | .[0].id // empty
  ' <<<"$keys_json")"

  if [[ -z "$KEY_ID" ]]; then
    echo "Chave habilitada $KEY_NAME não encontrada." >&2
    return 1
  fi
}

# Aguarda um Secret concluir uma operação e retornar ao estado ACTIVE.
wait_for_secret_active() {
  local secret_id="$1"
  local secret_name="$2"
  local secret_state
  local attempt
  local max_attempts=60

  for ((attempt = 1; attempt <= max_attempts; attempt++)); do
    secret_state="$(oci_cli vault secret get \
      --secret-id "$secret_id" \
      --query 'data."lifecycle-state"' \
      --raw-output)"

    case "$secret_state" in
      ACTIVE)
        return 0
        ;;

      FAILED|DELETED)
        echo "O Secret $secret_name chegou ao estado $secret_state." >&2
        return 1
        ;;

      *)
        echo "Aguardando o Secret $secret_name ficar ativo: estado $secret_state ($attempt/$max_attempts)..." >&2
        sleep 5
        ;;

    esac
  done

  echo "O Secret $secret_name não ficou ativo dentro de 5 minutos." >&2
  return 1
}

# Retorna o OCID reutilizável do Secret e normaliza estados transitórios.
resolve_secret_id() {
  local secret_name="$1"
  local secrets_json
  local secret_id
  local secret_state

  secrets_json="$(oci_cli vault secret list \
    --compartment-id "$COMPARTMENT_ID" \
    --vault-id "$VAULT_ID" \
    --name "$secret_name" \
    --all)"

  secret_id="$(jq -r '
    [.data[] | select(."lifecycle-state" != "DELETED")]
    | sort_by(."time-created") | reverse | .[0].id // empty
  ' <<<"$secrets_json")"

  if [[ -z "$secret_id" ]]; then
    return 0
  fi

  secret_state="$(jq -r --arg id "$secret_id" \
    '.data[] | select(.id == $id) | ."lifecycle-state"' <<<"$secrets_json")"

  case "$secret_state" in
    ACTIVE)
      ;;

    CREATING|UPDATING|CANCELLING_DELETION)
      wait_for_secret_active "$secret_id" "$secret_name"
      ;;

    PENDING_DELETION|SCHEDULING_DELETION)
      echo "Cancelando a exclusão agendada do Secret $secret_name..." >&2
      oci_cli vault secret cancel-secret-deletion --secret-id "$secret_id" >/dev/null
      wait_for_secret_active "$secret_id" "$secret_name"
      ;;

    *)
      echo "O Secret $secret_name está no estado $secret_state e não pode ser reutilizado." >&2
      return 1
      ;;

  esac

  printf '%s' "$secret_id"
}

# Executa uma criação sem expor o conteúdo do Secret na lista de processos.
create_secret() (
  local secret_name="$1"
  local description="$2"
  local secret_content="$3"
  local encoded_content
  local request_file
  local description_json
  local command_output

  # Garante a remoção do arquivo mesmo se a OCI CLI falhar ou for interrompida.
  cleanup_create_request() {
    if [[ -n "$request_file" && -f "$request_file" ]]; then
      rm -f -- "$request_file"
    fi
  }

  request_file=""
  trap cleanup_create_request EXIT

  display_secret_banner "Criando e salvando o Secret $secret_name no OCI Vault"

  encoded_content="$(printf '%s' "$secret_content" | base64 | tr -d '\n')"
  description_json="$(jq -Rn --arg value "$description" '$value')"
  request_file="$(mktemp)"
  chmod 600 "$request_file"

  printf '{"compartmentId":"%s","vaultId":"%s","keyId":"%s","secretName":"%s","description":%s,"secretContentContent":"%s"}' \
    "$COMPARTMENT_ID" "$VAULT_ID" "$KEY_ID" "$secret_name" \
    "$description_json" "$encoded_content" >"$request_file"

  if ! command_output="$(oci_cli vault secret create-base64 \
    --from-json "file://$request_file" \
    --wait-for-state ACTIVE \
    --query 'data.id' \
    --raw-output)"; then
    return 1
  fi

  printf '%s' "$command_output"
)

# Cria um Secret somente quando ainda não houver um Secret ativo com o nome.
create_secret_if_absent() {
  local secret_name="$1"
  local description="$2"
  local secret_content="$3"
  local secret_id

  secret_id="$(resolve_secret_id "$secret_name")"

  if [[ -n "$secret_id" ]]; then
    echo "Secret $secret_name já existe; mantendo o conteúdo atual." >&2
    printf '%s' "$secret_id"
    return 0
  fi

  create_secret "$secret_name" "$description" "$secret_content"
}

# Gera o conteúdo apenas quando o Secret ainda não puder ser reutilizado.
create_generated_secret_if_absent() {
  local secret_name="$1"
  local description="$2"
  local generator_function="$3"
  local secret_id
  local secret_content

  secret_id="$(resolve_secret_id "$secret_name")"

  if [[ -n "$secret_id" ]]; then
    echo "Secret $secret_name já existe; mantendo o conteúdo atual." >&2
    printf '%s' "$secret_id"
    return 0
  fi

  secret_content="$($generator_function)"
  create_secret "$secret_name" "$description" "$secret_content"
}

# Recupera e decodifica a versão CURRENT do Secret informado.
read_secret_content() {
  local secret_id="$1"

  oci_cli secrets secret-bundle get \
    --secret-id "$secret_id" \
    --stage CURRENT \
    --query 'data."secret-bundle-content".content' \
    --raw-output | base64 --decode
}

# Cria uma nova versão apenas quando o conteúdo desejado tiver mudado.
upsert_secret() (
  local secret_name="$1"
  local description="$2"
  local secret_content="$3"
  local secret_id
  local desired_content
  local current_content
  local request_file

  # Garante a remoção do arquivo mesmo se a OCI CLI falhar ou for interrompida.
  cleanup_update_request() {
    if [[ -n "$request_file" && -f "$request_file" ]]; then
      rm -f -- "$request_file"
    fi
  }

  request_file=""
  trap cleanup_update_request EXIT

  secret_id="$(resolve_secret_id "$secret_name")"

  if [[ -z "$secret_id" ]]; then
    create_secret "$secret_name" "$description" "$secret_content" >/dev/null
    return 0
  fi

  desired_content="$(printf '%s' "$secret_content" | base64 | tr -d '\n')"
  current_content="$(oci_cli secrets secret-bundle get \
    --secret-id "$secret_id" \
    --stage CURRENT \
    --query 'data."secret-bundle-content".content' \
    --raw-output)"

  if [[ "$current_content" == "$desired_content" ]]; then
    echo "Secret $secret_name já está atualizado; nenhuma alteração necessária."
    return 0
  fi

  request_file="$(mktemp)"
  chmod 600 "$request_file"
  printf '{"secretId":"%s","secretContentContent":"%s"}' \
    "$secret_id" "$desired_content" >"$request_file"

  display_secret_banner "Atualizando o Secret $secret_name no OCI Vault"
  if ! oci_cli vault secret update-base64 \
    --from-json "file://$request_file" \
    --force \
    --wait-for-state ACTIVE >/dev/null; then
    return 1
  fi
)

# Cria ou recupera o Vault persistente usado pela aplicação.
ensure_vault() {
  local vaults_json
  local vault_id
  local vault_state

  vaults_json="$(oci_cli kms management vault list \
    --compartment-id "$COMPARTMENT_ID" \
    --all)"

  vault_id="$(jq -r --arg name "$VAULT_NAME" '
    [.data[] | select(."display-name" == $name and ."lifecycle-state" != "DELETED")]
    | sort_by(."time-created") | reverse | .[0].id // empty
  ' <<<"$vaults_json")"

  if [[ -z "$vault_id" ]]; then
    echo "Criando o Vault $VAULT_NAME..." >&2
    oci_cli kms management vault create \
      --compartment-id "$COMPARTMENT_ID" \
      --display-name "$VAULT_NAME" \
      --vault-type DEFAULT \
      --wait-for-state ACTIVE \
      --query 'data.id' \
      --raw-output
    return 0
  fi

  vault_state="$(jq -r --arg id "$vault_id" '.data[] | select(.id == $id) | ."lifecycle-state"' <<<"$vaults_json")"

  case "$vault_state" in
    ACTIVE)
      echo "Vault $VAULT_NAME já existe; nenhuma criação necessária." >&2
      ;;

    CREATING|UPDATING)
      echo "Aguardando o Vault $VAULT_NAME ficar ativo..." >&2
      oci_cli kms management vault get --vault-id "$vault_id" --wait-for-state ACTIVE >/dev/null
      ;;

    PENDING_DELETION|SCHEDULING_DELETION)
      echo "Cancelando a exclusão agendada do Vault $VAULT_NAME..." >&2
      oci_cli kms management vault cancel-deletion \
        --vault-id "$vault_id" \
        --wait-for-state ACTIVE >/dev/null
      ;;

    *)
      echo "O Vault $VAULT_NAME está no estado $vault_state e não pode ser reutilizado." >&2
      return 1
      ;;

  esac

  printf '%s' "$vault_id"
}

# Cria, habilita ou recupera a chave AES-256 protegida por HSM.
ensure_vault_key() {
  local vault_id="$1"
  local vault_json
  local management_endpoint
  local keys_json
  local key_id
  local key_state

  vault_json="$(oci_cli kms management vault get --vault-id "$vault_id")"
  management_endpoint="$(jq -r '.data."management-endpoint"' <<<"$vault_json")"
  keys_json="$(oci_cli kms management key list \
    --endpoint "$management_endpoint" \
    --compartment-id "$COMPARTMENT_ID" \
    --all)"

  key_id="$(jq -r --arg name "$KEY_NAME" '
    [.data[] | select(."display-name" == $name and ."lifecycle-state" != "DELETED")]
    | sort_by(."time-created") | reverse | .[0].id // empty
  ' <<<"$keys_json")"

  if [[ -z "$key_id" ]]; then
    echo "Criando a chave $KEY_NAME..."

    oci_cli kms management key create \
      --endpoint "$management_endpoint" \
      --compartment-id "$COMPARTMENT_ID" \
      --display-name "$KEY_NAME" \
      --key-shape '{"algorithm":"AES","length":32}' \
      --protection-mode HSM \
      --wait-for-state ENABLED >/dev/null

    return 0
  fi

  key_state="$(jq -r --arg id "$key_id" '.data[] | select(.id == $id) | ."lifecycle-state"' <<<"$keys_json")"

  case "$key_state" in
    ENABLED)
      echo "Chave $KEY_NAME já existe; nenhuma criação necessária."
      ;;

    DISABLED)
      echo "Habilitando a chave $KEY_NAME..."
      oci_cli kms management key enable \
        --endpoint "$management_endpoint" \
        --key-id "$key_id" \
        --wait-for-state ENABLED >/dev/null
      ;;

    PENDING_DELETION|SCHEDULING_DELETION)
      echo "Cancelando a exclusão agendada da chave $KEY_NAME..."
      oci_cli kms management key cancel-deletion \
        --endpoint "$management_endpoint" \
        --key-id "$key_id" \
        --wait-for-state ENABLED >/dev/null
      ;;

    CREATING|ENABLING|UPDATING|CANCELLING_DELETION)
      echo "Aguardando a chave $KEY_NAME ficar habilitada..."
      oci_cli kms management key get \
        --endpoint "$management_endpoint" \
        --key-id "$key_id" \
        --wait-for-state ENABLED >/dev/null
      ;;

    *)
      echo "A chave $KEY_NAME está no estado $key_state e não pode ser reutilizada." >&2
      return 1
      ;;

  esac
}

# Executa a criação idempotente do Vault quando o arquivo é chamado diretamente.
main() {
  local action="${1:-apply}"
  local vault_id

  if [[ "$action" == "destroy" ]]; then
    echo "Vault e chave são persistentes; nenhuma ação será executada no destroy."
    return 0
  fi

  if [[ "$action" != "apply" ]]; then
    echo "Ação inválida: $action. Use apply ou destroy." >&2
    return 1
  fi

  : "${COMPARTMENT_ID:?Defina COMPARTMENT_ID.}"
  : "${OCI_REGION:?Defina OCI_REGION.}"

  validate_commands oci jq
  configure_oci_cli
  vault_id="$(ensure_vault)"
  ensure_vault_key "$vault_id"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  set -euo pipefail
  main "$@"
fi
