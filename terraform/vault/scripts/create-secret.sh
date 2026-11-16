#!/usr/bin/env bash

# Cria o Secret do PAT do GitHub ou cria uma nova versão quando seu conteúdo
# mudar. O Secret permanece intacto durante o terraform destroy.

set -euo pipefail

ACTION="${1:-apply}"
VAULT_NAME="ocipizza-vault"
KEY_NAME="ocipizza-vault-key"
SECRET_NAME="ocipizza-github-pat"
OCI_OPTIONS=()

# Centraliza as opções comuns para todas as chamadas da OCI CLI.
oci_cli() {
  oci "${OCI_OPTIONS[@]}" "$@"
}

# O comando get do Secret não oferece --wait-for-state. Esta função consulta
# o estado até a OCI concluir uma criação, atualização ou cancelamento.
wait_for_secret_active() {
  local secret_to_wait="$1"
  local secret_state
  local attempt
  local max_attempts=60

  for ((attempt = 1; attempt <= max_attempts; attempt++)); do
    secret_state="$(oci_cli vault secret get \
      --secret-id "$secret_to_wait" \
      --query 'data."lifecycle-state"' \
      --raw-output)"

    case "$secret_state" in
      ACTIVE)
        return 0
        ;;

      FAILED|DELETED)
        echo "O Secret $SECRET_NAME chegou ao estado $secret_state." >&2
        return 1
        ;;

      *)
        echo "Aguardando o Secret $SECRET_NAME ficar ativo: estado $secret_state ($attempt/$max_attempts)..."
        sleep 5
        ;;
        
    esac
  done

  echo "O Secret $SECRET_NAME não ficou ativo dentro de 5 minutos." >&2
  return 1
}

# No destroy, preserva o Secret para que ele possa ser reutilizado por uma
# nova criação da infraestrutura.
if [[ "$ACTION" == "destroy" ]]; then
  echo "Secret do GitHub é persistente; nenhuma ação será executada no destroy."
  exit 0
fi

# Impede a execução com uma ação diferente das previstas pelo Terraform.
if [[ "$ACTION" != "apply" ]]; then
  echo "Ação inválida: $ACTION. Use apply ou destroy." >&2
  exit 1
fi

# Confirma as entradas obrigatórias sem imprimir o PAT no terminal.
: "${COMPARTMENT_ID:?Defina COMPARTMENT_ID.}"
: "${OCI_REGION:?Defina OCI_REGION.}"
: "${GITHUB_PAT:?Defina GITHUB_PAT.}"

# Verifica as ferramentas necessárias para consultar a OCI e codificar o PAT.
for command in oci jq base64; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "O comando $command é obrigatório." >&2
    exit 1
  fi
done

# Reaproveita, quando informado, o mesmo profile e arquivo de configuração
# usados na autenticação local do provider OCI.
OCI_OPTIONS=(--region "$OCI_REGION")

if [[ -n "${OCI_CONFIG_FILE_PROFILE:-}" ]]; then
  OCI_OPTIONS+=(--profile "$OCI_CONFIG_FILE_PROFILE")
fi

if [[ -n "${OCI_CONFIG_FILE:-}" ]]; then
  OCI_OPTIONS+=(--config-file "$OCI_CONFIG_FILE")
fi

# Localiza o Vault ativo criado pelo create-vault.sh. O script não cria o
# Secret enquanto esse pré-requisito não estiver disponível.
vaults_json="$(oci_cli kms management vault list \
  --compartment-id "$COMPARTMENT_ID" \
  --all)"

vault_id="$(jq -r --arg name "$VAULT_NAME" '
  [.data[] | select(."display-name" == $name and ."lifecycle-state" == "ACTIVE")]
  | sort_by(."time-created") | reverse | .[0].id // empty
' <<<"$vaults_json")"

if [[ -z "$vault_id" ]]; then
  echo "Vault ativo $VAULT_NAME não encontrado. Execute create-vault.sh primeiro." >&2
  exit 1
fi

# Obtém o endpoint usado para consultar as Master Encryption Keys do Vault.
vault_json="$(oci_cli kms management vault get --vault-id "$vault_id")"
management_endpoint="$(jq -r '.data."management-endpoint"' <<<"$vault_json")"

# Localiza a chave habilitada que será usada para criptografar o Secret.
keys_json="$(oci_cli kms management key list \
  --endpoint "$management_endpoint" \
  --compartment-id "$COMPARTMENT_ID" \
  --all)"

key_id="$(jq -r --arg name "$KEY_NAME" '
  [.data[] | select(."display-name" == $name and ."lifecycle-state" == "ENABLED")]
  | sort_by(."time-created") | reverse | .[0].id // empty
' <<<"$keys_json")"

if [[ -z "$key_id" ]]; then
  echo "Chave habilitada $KEY_NAME não encontrada. Execute create-vault.sh primeiro." >&2
  exit 1
fi

# Procura o Secret pelo nome, incluindo estados transitórios e de exclusão,
# para evitar criar outro recurso enquanto o anterior ainda existe.
secrets_json="$(oci_cli vault secret list \
  --compartment-id "$COMPARTMENT_ID" \
  --vault-id "$vault_id" \
  --name "$SECRET_NAME" \
  --all)"

secret_id="$(jq -r '
  [.data[] | select(."lifecycle-state" != "DELETED")]
  | sort_by(."time-created") | reverse | .[0].id // empty
' <<<"$secrets_json")"

# A API do Vault recebe o conteúdo do Secret codificado em Base64.
desired_content="$(printf '%s' "$GITHUB_PAT" | base64 | tr -d '\n')"

# Cria o Secret somente quando nenhum recurso com esse nome pode ser
# reutilizado.
if [[ -z "$secret_id" ]]; then
  echo "Criando o Secret $SECRET_NAME..."

  oci_cli vault secret create-base64 \
    --compartment-id "$COMPARTMENT_ID" \
    --vault-id "$vault_id" \
    --key-id "$key_id" \
    --secret-name "$SECRET_NAME" \
    --description "PAT do GitHub usado pelo OCI DevOps do OCI Pizza." \
    --secret-content-content "$desired_content" \
    --wait-for-state ACTIVE >/dev/null

  exit 0
fi

# Normaliza o estado do Secret existente: aguarda operações em andamento ou
# cancela sua exclusão antes de tentar consultar e atualizar seu conteúdo.
secret_state="$(jq -r --arg id "$secret_id" '.data[] | select(.id == $id) | ."lifecycle-state"' <<<"$secrets_json")"

case "$secret_state" in
  ACTIVE)
    ;;

  CREATING|UPDATING|CANCELLING_DELETION)
    echo "Aguardando o Secret $SECRET_NAME ficar ativo..."

    wait_for_secret_active "$secret_id"
    ;;

  PENDING_DELETION|SCHEDULING_DELETION)
    echo "Cancelando a exclusão agendada do Secret $SECRET_NAME..."

    oci_cli vault secret cancel-secret-deletion \
      --secret-id "$secret_id" >/dev/null

    wait_for_secret_active "$secret_id"
    ;;

  *)
    echo "O Secret $SECRET_NAME está no estado $secret_state e não pode ser reutilizado." >&2
    exit 1
    ;;
esac

# Lê somente a versão CURRENT para evitar criar uma nova versão quando o PAT
# informado já for igual ao conteúdo armazenado.
current_content="$(oci_cli secrets secret-bundle get \
  --secret-id "$secret_id" \
  --stage CURRENT \
  --query 'data."secret-bundle-content".content' \
  --raw-output)"

if [[ "$current_content" == "$desired_content" ]]; then
  echo "Secret $SECRET_NAME já está atualizado; nenhuma alteração necessária."
  exit 0
fi

# A atualização do conteúdo cria uma nova versão CURRENT no mesmo Secret.
echo "Atualizando o Secret $SECRET_NAME com uma nova versão..."

oci_cli vault secret update-base64 \
  --secret-id "$secret_id" \
  --secret-content-content "$desired_content" \
  --force \
  --wait-for-state ACTIVE >/dev/null

exit 0
