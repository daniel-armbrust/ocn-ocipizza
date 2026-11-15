#!/usr/bin/env bash

#
# resource-manager-source-provider-destroy.sh
#
# Propósito:
# ----------
#
#   Remove o Configuration Source Provider criado pelo bootstrap do OCI Pizza.
#   O Terraform executa este script automaticamente durante o terraform destroy.
#   Se o provider já não existir, o script encerra sem erro.
#
# Variáveis recebidas do Terraform:
# ---------------------------------
#
#   RESOURCE_MANAGER_COMPARTMENT_ID
#     OCID do compartment onde o Configuration Source Provider foi criado.
#

set -euo pipefail

readonly CONFIGURATION_SOURCE_NAME="github-ocipizza"

required_commands=(oci jq)
required_variables=(RESOURCE_MANAGER_COMPARTMENT_ID)

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
      | select(."lifecycle-state" != "DELETED")
      | .id' <<<"${configuration_sources_json}"
)

if (( ${#configuration_source_ids[@]} == 0 )); then
  exit 0
fi

if (( ${#configuration_source_ids[@]} > 1 )); then
  echo "Mais de um Configuration Source Provider ativo foi encontrado com o nome ${CONFIGURATION_SOURCE_NAME}." >&2
  exit 1
fi

oci resource-manager configuration-source-provider delete \
  --configuration-source-provider-id "${configuration_source_ids[0]}" \
  --force

exit 0