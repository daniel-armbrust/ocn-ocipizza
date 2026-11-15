#!/usr/bin/env bash

#
# resource-manager-stack-destroy.sh
#
# Propósito:
# ----------
#
#   Remove a stack do OCI Pizza antes da exclusão do Configuration Source
#   Provider associado. O Terraform executa este script automaticamente durante
#   o terraform destroy. Se a stack já não existir, o script encerra sem erro.
#
# Variáveis recebidas do Terraform:
# ---------------------------------
#
#   RESOURCE_MANAGER_COMPARTMENT_ID
#     OCID do compartment onde a stack foi criada.
#
#   RESOURCE_MANAGER_STACK_NAME
#     Nome da stack que será removida.
#

set -euo pipefail

required_commands=(oci jq)
required_variables=(
  RESOURCE_MANAGER_COMPARTMENT_ID
  RESOURCE_MANAGER_STACK_NAME
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

if (( ${#stack_ids[@]} == 0 )); then
  exit 0
fi

if (( ${#stack_ids[@]} > 1 )); then
  echo "Mais de uma stack ativa foi encontrada com o nome ${RESOURCE_MANAGER_STACK_NAME}." >&2
  exit 1
fi

oci resource-manager stack delete \
  --stack-id "${stack_ids[0]}" \
  --force \
  --wait-for-state DELETED

exit 0