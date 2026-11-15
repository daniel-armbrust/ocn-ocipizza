#!/usr/bin/env bash

#
# resource-manager-config.sh
#
# Propósito:
# ----------
#
#   Este script prepara a stack do OCI Pizza no OCI Resource Manager. Ele
#   conecta a stack ao repositório do projeto no GitHub, escolhe a branch e
#   informa que o código Terraform responsável pela infraestrutura multi-região
#   está no diretório "terraform/infrastructure".
#
#   Após a execução deste script, a stack estará pronta. Quando um usuário
#   iniciar um job de Plan ou Apply, o OCI Resource Manager baixará o código do
#   GitHub e executará o Terraform para criar ou atualizar a infraestrutura do
#   OCI Pizza.
#
# Variáveis recebidas do Terraform:
# ---------------------------------
#
#   O local-exec fornece estas variáveis automaticamente durante o terraform
#   apply. O usuário define as entradas correspondentes com o prefixo TF_VAR_ e
#   não precisa executar este script manualmente.
#
#   RESOURCE_MANAGER_COMPARTMENT_ID
#     OCID do compartment onde a stack será criada ou consultada.
#
#   INFRASTRUCTURE_COMPARTMENT_ID
#     OCID do compartment onde a infraestrutura do OCI Pizza será criada.
#
#   FIREWALL_SSH_PUBLIC_KEY
#     Conteúdo da chave pública SSH usada pelo firewall.
#
#   OKE_WORKER_SSH_PUBLIC_KEY
#     Conteúdo da chave pública SSH usada pelos worker nodes do OKE.
#

set -euo pipefail

readonly CONFIGURATION_SOURCE_NAME="github-ocipizza"
readonly RESOURCE_MANAGER_COMPARTMENT_ID="${RESOURCE_MANAGER_COMPARTMENT_ID:-${COMPARTMENT_ID:-}}"
readonly RESOURCE_MANAGER_STACK_NAME="${RESOURCE_MANAGER_STACK_NAME:-ocipizza-infrastructure}"
readonly RESOURCE_MANAGER_REPOSITORY_URL="${RESOURCE_MANAGER_REPOSITORY_URL:-https://github.com/daniel-armbrust/ocn-ocipizza.git}"
readonly RESOURCE_MANAGER_REPOSITORY_BRANCH="${RESOURCE_MANAGER_REPOSITORY_BRANCH:-main}"
readonly RESOURCE_MANAGER_WORKING_DIRECTORY="${RESOURCE_MANAGER_WORKING_DIRECTORY:-terraform/infrastructure}"
readonly RESOURCE_MANAGER_TERRAFORM_VERSION="${RESOURCE_MANAGER_TERRAFORM_VERSION:-1.5.x}"

# Comandos e variáveis necessários para que a configuração seja determinística.
required_commands=(oci jq)

required_variables=(
  RESOURCE_MANAGER_COMPARTMENT_ID
  INFRASTRUCTURE_COMPARTMENT_ID
  FIREWALL_SSH_PUBLIC_KEY
  OKE_WORKER_SSH_PUBLIC_KEY
)

for command_name in "${required_commands[@]}"; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Comando obrigatório não encontrado: ${command_name}" >&2
    exit 1
  fi
done

for variable_name in "${required_variables[@]}"; do
  if [[ -z "${!variable_name:-}" ]]; then
    echo "Variável de ambiente obrigatória não informada: ${variable_name}" >&2
    exit 1
  fi
done

# Obtém o OCID da conexão GitHub criada pelo script
# resource-manager-source-provider.sh.
configuration_sources_json="$(
  oci resource-manager configuration-source-provider list \
    --compartment-id "${RESOURCE_MANAGER_COMPARTMENT_ID}" \
    --display-name "${CONFIGURATION_SOURCE_NAME}" \
    --all
)"

mapfile -t configuration_source_ids < <(
  jq -r \
    '(.data | if type == "array" then . else (.items // []) end)[]
      | select(."config-source-provider-type" == "GITHUB_ACCESS_TOKEN")
      | select(."lifecycle-state" == "ACTIVE")
      | .id' <<<"${configuration_sources_json}"
)

if (( ${#configuration_source_ids[@]} != 1 )); then
  echo "Era esperado exatamente um Configuration Source Provider ativo com o nome ${CONFIGURATION_SOURCE_NAME}." >&2
  exit 1
fi

# O arquivo temporário evita manter no repositório uma cópia dos valores
# enviados como variáveis Terraform ao stack de infraestrutura.
stack_variables_file="$(mktemp)"
trap 'rm -f "${stack_variables_file}"' EXIT

jq -n \
  --arg compartment_id "${INFRASTRUCTURE_COMPARTMENT_ID}" \
  --arg firewall_ssh_public_key "${FIREWALL_SSH_PUBLIC_KEY}" \
  --arg oke_worker_ssh_public_key "${OKE_WORKER_SSH_PUBLIC_KEY}" \
  '{
    compartment_id: $compartment_id,
    firewall_ssh_public_key: $firewall_ssh_public_key,
    oke_worker_ssh_public_key: $oke_worker_ssh_public_key
  }' >"${stack_variables_file}"

# A consulta pelo nome permite que execuções posteriores atualizem o mesmo
# stack em vez de criarem outro recurso.
stacks_json="$(
  oci resource-manager stack list \
      --compartment-id "${RESOURCE_MANAGER_COMPARTMENT_ID}" \
      --all
)"

mapfile -t stack_ids < <(
  jq -r \
    --arg stack_name "${RESOURCE_MANAGER_STACK_NAME}" \
    '(.data | if type == "array" then . else (.items // []) end)[]
      | select(."display-name" == $stack_name)
      | select(."lifecycle-state" != "DELETED")
      | .id' <<<"${stacks_json}"
)

if (( ${#stack_ids[@]} > 1 )); then
  echo "Mais de um stack ativo foi encontrado com o nome ${RESOURCE_MANAGER_STACK_NAME}." >&2
  exit 1
fi

# Argumentos comuns mantêm a criação e a atualização com a mesma origem Git,
# versão do Terraform, working directory e conjunto de variáveis.
common_arguments=(
  --config-source-configuration-source-provider-id "${configuration_source_ids[0]}"
  --config-source-repository-url "${RESOURCE_MANAGER_REPOSITORY_URL}"
  --config-source-branch-name "${RESOURCE_MANAGER_REPOSITORY_BRANCH}"
  --config-source-working-directory "${RESOURCE_MANAGER_WORKING_DIRECTORY}"
  --display-name "${RESOURCE_MANAGER_STACK_NAME}"
  --description "Infraestrutura multirregião do OCI Pizza"
  --terraform-version "${RESOURCE_MANAGER_TERRAFORM_VERSION}"
  --variables "file://${stack_variables_file}"
)

# O stack é criado somente na primeira execução. Nas seguintes, sua
# configuração é atualizada com os valores recebidos pelo bootstrap.
if (( ${#stack_ids[@]} == 0 )); then
  oci resource-manager stack create-from-git-provider \
    --compartment-id "${RESOURCE_MANAGER_COMPARTMENT_ID}" \
    "${common_arguments[@]}" \
    --wait-for-state SUCCEEDED
else
  oci resource-manager stack update-from-git-provider \
    --stack-id "${stack_ids[0]}" \
    "${common_arguments[@]}" \
    --force \
    --wait-for-state ACTIVE
fi

exit 0
