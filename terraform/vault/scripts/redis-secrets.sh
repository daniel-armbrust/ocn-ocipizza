#!/usr/bin/env bash

# Gera credenciais dos consumidores do OCI Cache, armazena o texto claro no
# OCI Vault e configura os usuários regionais usando somente o hash SHA-256.

set -euo pipefail

ACTION="${1:-apply}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ACL_STRING="~* &* +@read +@write +@connection +@keyspace +@transaction"
TEMPORARY_DIRECTORY=""
OCI_CACHE_USER_IDS=()

# Carrega as funções compartilhadas de integração com o OCI Vault.
source "$SCRIPT_DIR/vault.sh"

# Remove os arquivos temporários usados nas chamadas da OCI CLI.
cleanup_temporary_directory() {
  if [[ -n "$TEMPORARY_DIRECTORY" && -d "$TEMPORARY_DIRECTORY" ]]; then
    rm -f -- "$TEMPORARY_DIRECTORY"/*.json
    rmdir -- "$TEMPORARY_DIRECTORY"
  fi
}

# Gera uma senha hexadecimal de 384 bits, segura também para uso em uma URI.
generate_redis_password() {
  openssl rand -hex 48
}

# Lê ou cria no Vault o documento JSON com usuário e senha do consumidor.
ensure_redis_credentials() {
  local environment="$1"
  local service_name="$2"
  local username="${service_name}-${environment}"
  local secret_name="ocipizza-${environment}-${service_name}-redis-credentials"
  local secret_id
  local password
  local credentials

  secret_id="$(resolve_secret_id "$secret_name")"

  if [[ -z "$secret_id" ]]; then
    password="$(generate_redis_password)"
    credentials="$(jq -cn \
      --arg username "$username" \
      --arg password "$password" \
      '{username: $username, password: $password}')"

    secret_id="$(create_secret \
      "$secret_name" \
      "Credenciais Redis do $service_name no ambiente $environment." \
      "$credentials")"
  fi

  read_secret_content "$secret_id"
}

# Localiza o usuário regional mais recente com o nome informado.
find_oci_cache_user() {
  local username="$1"

  oci_cli redis oci-cache-user oci-cache-user-summary list-oci-cache-users \
    --compartment-id "$COMPARTMENT_ID" \
    --name "$username" \
    --all | jq -c --arg username "$username" \
    '[.data.items[] | select(.name == $username)]
      | sort_by(."time-created") | last // {}'
}

# Aguarda a conclusão da criação ou atualização e exibe a causa de falhas.
wait_for_oci_cache_user() {
  local username="$1"
  local attempt
  local user
  local user_id
  local lifecycle_state
  local lifecycle_details

  for ((attempt = 1; attempt <= 60; attempt++)); do
    user="$(find_oci_cache_user "$username")"
    user_id="$(jq -r '.id // empty' <<<"$user")"
    lifecycle_state="$(jq -r '."lifecycle-state" // empty' <<<"$user")"
    lifecycle_details="$(jq -r '."lifecycle-details" // empty' <<<"$user")"

    case "$lifecycle_state" in
      ACTIVE)
        printf '%s\n' "$user_id"
        return 0
        ;;

      FAILED)
        echo "A configuração do OCI Cache User $username falhou: ${lifecycle_details:-motivo não informado pela OCI}." >&2
        return 1
        ;;

      CREATING | UPDATING | "")
        sleep 10
        ;;

      *)
        echo "Estado inesperado do OCI Cache User $username: $lifecycle_state." >&2
        return 1
        ;;

    esac
  done

  echo "Tempo limite excedido ao aguardar o OCI Cache User $username ficar ACTIVE." >&2
  return 1
}

# Cria um OCI Cache User ausente ou reutiliza o usuário regional ativo.
ensure_oci_cache_user() {
  local environment="$1"
  local service_name="$2"
  local credentials="$3"
  local username
  local password
  local password_hash
  local user_id
  local user
  local lifecycle_state
  local request_file

  username="$(jq -er '.username' <<<"$credentials")"
  password="$(jq -er '.password' <<<"$credentials")"
  password_hash="$(printf '%s' "$password" | sha256sum | cut -d ' ' -f 1)"
  user="$(find_oci_cache_user "$username")"
  user_id="$(jq -r '.id // empty' <<<"$user")"
  lifecycle_state="$(jq -r '."lifecycle-state" // empty' <<<"$user")"

  if [[ "$lifecycle_state" == "FAILED" ]]; then
    echo "Já existe um OCI Cache User $username em estado FAILED: $(jq -r '."lifecycle-details" // "motivo não informado pela OCI"' <<<"$user")." >&2
    return 1
  fi

  if [[ "$lifecycle_state" == "CREATING" || "$lifecycle_state" == "UPDATING" ]]; then
    echo "Aguardando a operação pendente do OCI Cache User $username em $OCI_CACHE_REGION..."
    user_id="$(wait_for_oci_cache_user "$username")"
    lifecycle_state="ACTIVE"
  fi

  if [[ -z "$user_id" ]]; then
    request_file="$TEMPORARY_DIRECTORY/create-${username}.json"
    jq -cn \
      --arg name "$username" \
      --arg description "Usuário Redis do $service_name no ambiente $environment." \
      --arg compartment_id "$COMPARTMENT_ID" \
      --arg acl_string "$ACL_STRING" \
      --arg password_hash "$password_hash" \
      '{name: $name, description: $description, compartmentId: $compartment_id,
        aclString: $acl_string, authenticationModeHashedPasswords: [$password_hash],
        status: "ON"}' >"$request_file"

    echo "Criando o OCI Cache User $username em $OCI_CACHE_REGION..."
    oci_cli redis oci-cache-user create-oci-cache-user-details \
      create-oci-cache-user-password-authentication-mode \
      --from-json "file://$request_file" >/dev/null

    user_id="$(wait_for_oci_cache_user "$username")"
  else
    echo "OCI Cache User $username já está ativo em $OCI_CACHE_REGION; mantendo a configuração atual."
  fi

  if [[ -z "$user_id" ]]; then
    echo "Não foi possível localizar o OCI Cache User $username após a configuração." >&2
    return 1
  fi

  if printf '%s\n' "${OCI_CACHE_USER_IDS[@]}" | grep -Fxq -- "$user_id"; then
    echo "O OCID $user_id foi resolvido para mais de um OCI Cache User; a associação foi interrompida." >&2
    return 1
  fi

  OCI_CACHE_USER_IDS+=("$user_id")
}

# Lista os usuários associados e normaliza a resposta vazia da OCI CLI.
list_attached_oci_cache_users() {
  local attached_users_json

  attached_users_json="$(oci_cli redis redis-cluster attached-oci-cache-user list \
    --redis-cluster-id "$OCI_CACHE_CLUSTER_ID" \
    --compartment-id "$COMPARTMENT_ID" \
    --all)"

  if [[ -z "$attached_users_json" ]]; then
    printf '%s\n' '{"data":[]}'
    return 0
  fi

  if ! jq -e . >/dev/null 2>&1 <<<"$attached_users_json"; then
    echo "A OCI CLI retornou uma resposta inválida ao listar os usuários associados ao cluster." >&2
    return 1
  fi

  printf '%s\n' "$attached_users_json"
}

# Aguarda o cluster aceitar uma nova operação de associação de usuários.
wait_for_oci_cache_cluster_active() {
  local attempt
  local cluster_json
  local lifecycle_state
  local lifecycle_details

  for ((attempt = 1; attempt <= 360; attempt++)); do
    cluster_json="$(oci_cli redis redis-cluster redis-cluster get \
      --redis-cluster-id "$OCI_CACHE_CLUSTER_ID")"
    lifecycle_state="$(jq -r '.data."lifecycle-state" // empty' <<<"$cluster_json")"
    lifecycle_details="$(jq -r '.data."lifecycle-details" // empty' <<<"$cluster_json")"

    case "$lifecycle_state" in
      ACTIVE)
        return 0
        ;;

      CREATING | UPDATING)
        echo "Aguardando o OCI Cache cluster ficar ACTIVE: estado $lifecycle_state ($attempt/360)..." >&2
        sleep 10
        ;;

      FAILED | DELETING | DELETED)
        echo "O OCI Cache cluster está no estado $lifecycle_state: ${lifecycle_details:-motivo não informado pela OCI}." >&2
        return 1
        ;;

      *)
        echo "Estado inesperado do OCI Cache cluster: ${lifecycle_state:-vazio}." >&2
        return 1
        ;;
        
    esac
  done

  echo "Tempo limite de 1 hora excedido ao aguardar o OCI Cache cluster ficar ACTIVE." >&2
  return 1
}

# Aguarda até que todos os usuários esperados apareçam associados ao cluster.
wait_for_oci_cache_users_attached() {
  local attempt
  local attached_users_json
  local missing_user_count

  for ((attempt = 1; attempt <= 60; attempt++)); do
    attached_users_json="$(list_attached_oci_cache_users)"

    missing_user_count="$(printf '%s\n' "${OCI_CACHE_USER_IDS[@]}" | jq -Rsc \
      --argjson attached "$attached_users_json" '
        split("\n")[:-1]
        | map(select(. as $id | ($attached.data // [])
            | map(."oci-cache-user-id") | index($id) | not))
        | length
      ')"

    if [[ "$missing_user_count" == "0" ]]; then
      return 0
    fi

    sleep 10
  done

  echo "Tempo limite excedido ao associar os OCI Cache Users ao cluster $OCI_CACHE_CLUSTER_ID." >&2
  return 1
}

# Associa ao cluster somente os usuários que ainda não estiverem anexados.
attach_oci_cache_users() {
  local attached_users_json
  local attach_output
  local attempt
  local missing_user_ids_json
  local request_file

  request_file="$TEMPORARY_DIRECTORY/attach-users.json"
  for ((attempt = 1; attempt <= 6; attempt++)); do
    wait_for_oci_cache_cluster_active

    attached_users_json="$(list_attached_oci_cache_users)"
    missing_user_ids_json="$(printf '%s\n' "${OCI_CACHE_USER_IDS[@]}" | jq -Rsc \
      --argjson attached "$attached_users_json" '
        split("\n")[:-1]
        | map(select(. as $id | ($attached.data // [])
            | map(."oci-cache-user-id") | index($id) | not))
      ')"

    if [[ "$missing_user_ids_json" == "[]" ]]; then
      echo "Usuários do OCI Cache já estão associados ao cluster regional."
      return 0
    fi

    jq -cn \
      --arg cluster_id "$OCI_CACHE_CLUSTER_ID" \
      --argjson user_ids "$missing_user_ids_json" \
      '{redisClusterId: $cluster_id, ociCacheUsers: $user_ids}' >"$request_file"

    echo "Associando os OCI Cache Users ao cluster $OCI_CACHE_CLUSTER_ID..."
    if attach_output="$(oci_cli redis redis-cluster redis-cluster attach \
      --from-json "file://$request_file" 2>&1)"; then
      wait_for_oci_cache_users_attached
      return 0
    fi

    if grep -Fq 'Cluster is in Updating state' <<<"$attach_output"; then
      echo "O cluster voltou ao estado UPDATING antes da associação; nova tentativa ($attempt/6)..." >&2
      sleep 10
      continue
    fi

    printf '%s\n' "$attach_output" >&2
    return 1
  done

  echo "Não foi possível associar os OCI Cache Users após 6 tentativas." >&2
  return 1
}

if [[ "$ACTION" == "destroy" ]]; then
  echo "Credenciais e OCI Cache Users são persistentes; nenhuma ação será executada no destroy."
  exit 0
fi

if [[ "$ACTION" != "apply" ]]; then
  echo "Ação inválida: $ACTION. Use apply ou destroy." >&2
  exit 1
fi

: "${COMPARTMENT_ID:?Defina COMPARTMENT_ID.}"
: "${OCI_CACHE_CLUSTER_ID:?Defina OCI_CACHE_CLUSTER_ID.}"
: "${OCI_CACHE_REGION:?Defina OCI_CACHE_REGION.}"
: "${VAULT_REGION:?Defina VAULT_REGION.}"

validate_commands oci jq base64 openssl sha256sum cut grep
display_secret_banner "Gerando e salvando as credenciais Redis no OCI Vault"

TEMPORARY_DIRECTORY="$(mktemp -d)"
chmod 700 "$TEMPORARY_DIRECTORY"
trap cleanup_temporary_directory EXIT

OCI_REGION="$VAULT_REGION"
configure_oci_cli
resolve_vault_resources

admin_homol_credentials="$(ensure_redis_credentials homol admin-service)"
admin_prod_credentials="$(ensure_redis_credentials prod admin-service)"
frontend_homol_credentials="$(ensure_redis_credentials homol frontend-service)"
frontend_prod_credentials="$(ensure_redis_credentials prod frontend-service)"

OCI_REGION="$OCI_CACHE_REGION"
configure_oci_cli

ensure_oci_cache_user homol admin-service "$admin_homol_credentials"
ensure_oci_cache_user prod admin-service "$admin_prod_credentials"
ensure_oci_cache_user homol frontend-service "$frontend_homol_credentials"
ensure_oci_cache_user prod frontend-service "$frontend_prod_credentials"
attach_oci_cache_users

echo "Credenciais e usuários Redis configurados em $OCI_CACHE_REGION."
