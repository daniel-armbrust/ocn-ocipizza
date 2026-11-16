#!/usr/bin/env bash

# Cria o Vault e a chave usados pelo OCI Pizza quando eles ainda não existem.
# Os recursos são persistentes e não são excluídos durante o terraform destroy.

set -euo pipefail

ACTION="${1:-apply}"
VAULT_NAME="ocipizza-vault"
KEY_NAME="ocipizza-vault-key"
OCI_OPTIONS=()

# Centraliza as opções comuns para todas as chamadas da OCI CLI.
oci_cli() {
  oci "${OCI_OPTIONS[@]}" "$@"
}

# No destroy, preserva os recursos que possuem ciclo de vida independente do
# restante da infraestrutura.
if [[ "$ACTION" == "destroy" ]]; then
  echo "Vault e chave são persistentes; nenhuma ação será executada no destroy."
  exit 0
fi

# Impede a execução com uma ação diferente das previstas pelo Terraform.
if [[ "$ACTION" != "apply" ]]; then
  echo "Ação inválida: $ACTION. Use apply ou destroy." >&2
  exit 1
fi

# Confirma as entradas obrigatórias antes de consultar a OCI.
: "${COMPARTMENT_ID:?Defina COMPARTMENT_ID.}"
: "${OCI_REGION:?Defina OCI_REGION.}"

# Verifica se as ferramentas utilizadas pelas consultas estão disponíveis.
for command in oci jq; do
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

# Procura o Vault pelo nome e seleciona o mais recente que ainda não tenha
# sido excluído definitivamente.
vaults_json="$(oci_cli kms management vault list \
  --compartment-id "$COMPARTMENT_ID" \
  --all)"

vault_id="$(jq -r --arg name "$VAULT_NAME" '
  [.data[] | select(."display-name" == $name and ."lifecycle-state" != "DELETED")]
  | sort_by(."time-created") | reverse | .[0].id // empty
' <<<"$vaults_json")"

# Cria um Vault padrão quando ele não existe. Quando existe, aguarda estados
# transitórios ou cancela uma exclusão agendada para permitir sua reutilização.
if [[ -z "$vault_id" ]]; then
  echo "Criando o Vault $VAULT_NAME..."

  vault_id="$(oci_cli kms management vault create \
    --compartment-id "$COMPARTMENT_ID" \
    --display-name "$VAULT_NAME" \
    --vault-type DEFAULT \
    --wait-for-state ACTIVE \
    --query 'data.id' \
    --raw-output)"
else
  vault_state="$(jq -r --arg id "$vault_id" '.data[] | select(.id == $id) | ."lifecycle-state"' <<<"$vaults_json")"

  case "$vault_state" in
    ACTIVE)
      echo "Vault $VAULT_NAME já existe; nenhuma criação necessária."
      ;;

    CREATING|UPDATING)
      echo "Aguardando o Vault $VAULT_NAME ficar ativo..."

      oci_cli kms management vault get --vault-id "$vault_id" --wait-for-state ACTIVE >/dev/null
      ;;

    PENDING_DELETION|SCHEDULING_DELETION)
      echo "Cancelando a exclusão agendada do Vault $VAULT_NAME..."

      oci_cli kms management vault cancel-deletion \
        --vault-id "$vault_id" \
        --wait-for-state ACTIVE >/dev/null
      ;;
  
    *)
      echo "O Vault $VAULT_NAME está no estado $vault_state e não pode ser reutilizado." >&2
      exit 1
      ;;

  esac
fi

# Obtém o endpoint específico do Vault exigido pelas operações de chave.
vault_json="$(oci_cli kms management vault get --vault-id "$vault_id")"
management_endpoint="$(jq -r '.data."management-endpoint"' <<<"$vault_json")"

# Procura pelo nome a chave mais recente que ainda possa ser recuperada.
keys_json="$(oci_cli kms management key list \
  --endpoint "$management_endpoint" \
  --compartment-id "$COMPARTMENT_ID" \
  --all)"

key_id="$(jq -r --arg name "$KEY_NAME" '
  [.data[] | select(."display-name" == $name and ."lifecycle-state" != "DELETED")]
  | sort_by(."time-created") | reverse | .[0].id // empty
' <<<"$keys_json")"

# Cria uma chave simétrica AES-256 protegida por HSM quando necessário. Para
# uma chave existente, restaura o estado ENABLED antes de finalizar.
if [[ -z "$key_id" ]]; then
  echo "Criando a chave $KEY_NAME..."

  oci_cli kms management key create \
    --endpoint "$management_endpoint" \
    --compartment-id "$COMPARTMENT_ID" \
    --display-name "$KEY_NAME" \
    --key-shape '{"algorithm":"AES","length":32}' \
    --protection-mode HSM \
    --wait-for-state ENABLED >/dev/null
else
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
      exit 1
      ;;

  esac
fi

exit 0
