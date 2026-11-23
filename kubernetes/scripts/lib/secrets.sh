#!/usr/bin/env bash

# Funções compartilhadas para materializar Secrets do OCI Vault no OKE.

VAULT_REGION="${VAULT_REGION:-sa-saopaulo-1}"
OCI_AUTH_MODE="${OCI_AUTH_MODE:-resource_principal}"
OCI_OPTIONS=()
SECRETS_TEMPORARY_DIRECTORY=""

# Valida se os comandos exigidos pelos scripts estão disponíveis.
validate_commands() {
  local command

  for command in "$@"; do
    if ! command -v "$command" >/dev/null 2>&1; then
      echo "O comando $command é obrigatório." >&2
      return 1
    fi
  done
}

# Valida o ambiente, a região e o namespace de destino do deployment.
validate_deployment_context() {
  if [[ ! "$ENVIRONMENT" =~ ^(homol|prod)$ ]]; then
    echo "ENVIRONMENT deve ser homol ou prod." >&2
    return 1
  fi

  if [[ ! "$REGION_KEY" =~ ^(gru|vcp)$ ]]; then
    echo "REGION_KEY deve ser gru ou vcp." >&2
    return 1
  fi

  if [[ "$KUBERNETES_NAMESPACE" != "ocipizza-$ENVIRONMENT" ]]; then
    echo "KUBERNETES_NAMESPACE deve ser ocipizza-$ENVIRONMENT." >&2
    return 1
  fi
}

# Valida o IP ou FQDN e a porta usados para montar a URI do Redis.
validate_redis_connection() {
  if [[ ! "$REDIS_HOST" =~ ^[A-Za-z0-9.-]+$ ]]; then
    echo "REDIS_HOST deve conter somente um IP ou FQDN válido." >&2
    return 1
  fi

  if [[ ! "$REDIS_PORT" =~ ^[0-9]+$ ]] || (( REDIS_PORT < 1 || REDIS_PORT > 65535 )); then
    echo "REDIS_PORT deve estar entre 1 e 65535." >&2
    return 1
  fi
}

# Configura as opções de autenticação e região da OCI CLI.
configure_oci_cli() {
  OCI_OPTIONS=(--region "$VAULT_REGION" --auth "$OCI_AUTH_MODE")

  if [[ -n "${OCI_CONFIG_FILE_PROFILE:-}" ]]; then
    OCI_OPTIONS+=(--profile "$OCI_CONFIG_FILE_PROFILE")
  fi

  if [[ -n "${OCI_CONFIG_FILE:-}" ]]; then
    OCI_OPTIONS+=(--config-file "$OCI_CONFIG_FILE")
  fi
}

# Centraliza as chamadas da OCI CLI sem imprimir o conteúdo dos secrets.
oci_cli() {
  oci "${OCI_OPTIONS[@]}" "$@"
}

# Lê e decodifica a versão CURRENT de um Secret pelo nome.
read_vault_secret() {
  local secret_name="$1"
  local encoded_content

  encoded_content="$(oci_cli secrets secret-bundle get-secret-bundle-by-name \
    --vault-id "$VAULT_ID" \
    --secret-name "$secret_name" \
    --stage CURRENT \
    --query 'data."secret-bundle-content".content' \
    --raw-output)"

  if [[ -z "$encoded_content" || "$encoded_content" == "null" || "$encoded_content" == "None" ]]; then
    echo "O Secret $secret_name não possui conteýo CURRENT." >&2
    return 1
  fi

  printf '%s' "$encoded_content" | base64 --decode
}

# Cria o diretório temporário protegido usado para montar os manifests.
prepare_temporary_directory() {
  SECRETS_TEMPORARY_DIRECTORY="$(mktemp -d)"
  chmod 700 "$SECRETS_TEMPORARY_DIRECTORY"
}

# Remove os arquivos temporários que contêm valores sensíveis.
cleanup_temporary_directory() {
  if [[ -n "$SECRETS_TEMPORARY_DIRECTORY" && -d "$SECRETS_TEMPORARY_DIRECTORY" ]]; then
    find "$SECRETS_TEMPORARY_DIRECTORY" -type f -exec rm -f -- {} +
    rmdir -- "$SECRETS_TEMPORARY_DIRECTORY"
  fi
}

# Cria ou atualiza um Secret Kubernetes a partir de pares chave e valor.
apply_kubernetes_secret() {
  local secret_name="$1"
  shift

  local key
  local value
  local value_file
  local manifest_file="$SECRETS_TEMPORARY_DIRECTORY/${secret_name}.json"
  local from_file_arguments=()

  if (( $# == 0 || $# % 2 != 0 )); then
    echo "O Secret $secret_name exige pares de chave e valor." >&2
    return 1
  fi

  while (( $# > 0 )); do
    key="$1"
    value="$2"
    shift 2

    if [[ ! "$key" =~ ^[A-Za-z0-9._-]+$ ]]; then
      echo "Chave inválida no Secret $secret_name: $key." >&2
      return 1
    fi

    value_file="$SECRETS_TEMPORARY_DIRECTORY/${secret_name}-${key}"
    printf '%s' "$value" >"$value_file"
    chmod 600 "$value_file"
    from_file_arguments+=(--from-file="$key=$value_file")
  done

  kubectl create secret generic "$secret_name" \
    --namespace "$KUBERNETES_NAMESPACE" \
    "${from_file_arguments[@]}" \
    --dry-run=client \
    --output json >"$manifest_file"
  chmod 600 "$manifest_file"

  kubectl apply \
    --server-side \
    --field-manager ocipizza-devops \
    --filename "$manifest_file" >/dev/null
  echo "Secret $secret_name aplicado no namespace $KUBERNETES_NAMESPACE."
}

# Inicializa e valida o contexto comum dos scripts de secrets.
initialize_secrets_script() {
  : "${ENVIRONMENT:?Defina ENVIRONMENT.}"
  : "${KUBERNETES_NAMESPACE:?Defina KUBERNETES_NAMESPACE.}"
  : "${REGION_KEY:?Defina REGION_KEY.}"
  : "${VAULT_ID:?Defina VAULT_ID.}"

  validate_commands oci kubectl jq base64 mktemp find
  validate_deployment_context
  configure_oci_cli

  if ! kubectl get namespace "$KUBERNETES_NAMESPACE" >/dev/null 2>&1; then
    echo "O namespace $KUBERNETES_NAMESPACE não existe no cluster selecionado." >&2
    echo "Aplique primeiro o namespace.yaml do overlay de $ENVIRONMENT/$REGION_KEY." >&2
    return 1
  fi

  prepare_temporary_directory
}
