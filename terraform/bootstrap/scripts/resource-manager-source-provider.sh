#!/usr/bin/env bash

#
# resource-manager-source-provider.sh
#
# Propósito:
# ----------
#
#   Criar ou atualizar o Configuration Source Provider que conecta o OCI
#   Resource Manager ao GitHub público utilizado pelo projeto OCI Pizza.
#
#   O provider Terraform oficial oracle/oci não disponibiliza um resource para
#   gerenciar Configuration Source Providers por isto, este script através de
#   OCI CLI executado por terraform local-exec, cria ou atualiza a conexão entre
#   o OCI Resource Manager e o GitHub.
#
# Variáveis utilizadas pelo Terraform:
# ------------------------------------
#
#   O local-exec fornece RESOURCE_MANAGER_COMPARTMENT_ID automaticamente durante
#   o terraform apply. GITHUB_ACCESS_TOKEN deve ser exportada no Linux local
#   antes do apply para não ser armazenada no state.
#
#   RESOURCE_MANAGER_COMPARTMENT_ID
#     OCID do compartment onde a conexão será criada ou consultada.
#
#   GITHUB_ACCESS_TOKEN
#     Personal Access Token usado pelo Resource Manager para ler o repositório.
#     Deve ser exportado antes do terraform apply.
#

set -euo pipefail

readonly CONFIGURATION_SOURCE_NAME="github-ocipizza"
readonly GITHUB_API_ENDPOINT="https://github.com"
readonly RESOURCE_MANAGER_COMPARTMENT_ID="${RESOURCE_MANAGER_COMPARTMENT_ID:-${COMPARTMENT_ID:-}}"

required_commands=(oci jq)

required_variables=(
  RESOURCE_MANAGER_COMPARTMENT_ID
  GITHUB_ACCESS_TOKEN
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

if (( ${#configuration_source_ids[@]} > 1 )); then
  echo "Mais de um Configuration Source Provider ativo foi encontrado com o nome ${CONFIGURATION_SOURCE_NAME}." >&2
  exit 1
fi

# Protege o PAT em um arquivo temporário e impede sua exposição nos argumentos
# do processo da OCI CLI.
umask 077
request_file="$(mktemp)"
trap 'rm -f "${request_file}"' EXIT

if (( ${#configuration_source_ids[@]} == 0 )); then
  jq -n \
    --arg access_token "${GITHUB_ACCESS_TOKEN}" \
    --arg api_endpoint "${GITHUB_API_ENDPOINT}" \
    --arg compartment_id "${RESOURCE_MANAGER_COMPARTMENT_ID}" \
    --arg display_name "${CONFIGURATION_SOURCE_NAME}" \
    '{
      accessToken: $access_token,
      apiEndpoint: $api_endpoint,
      compartmentId: $compartment_id,
      displayName: $display_name,
      description: "Conexão do OCI Resource Manager com o GitHub da OCI Pizza",
      waitForState: ["ACTIVE"]
    }' >"${request_file}"

  oci resource-manager configuration-source-provider \
    create-github-access-token-provider \
    --from-json "file://${request_file}"
else
  jq -n \
    --arg access_token "${GITHUB_ACCESS_TOKEN}" \
    --arg api_endpoint "${GITHUB_API_ENDPOINT}" \
    --arg configuration_source_provider_id "${configuration_source_ids[0]}" \
    --arg display_name "${CONFIGURATION_SOURCE_NAME}" \
    '{
      accessToken: $access_token,
      apiEndpoint: $api_endpoint,
      configurationSourceProviderId: $configuration_source_provider_id,
      displayName: $display_name,
      description: "Conexão do OCI Resource Manager com o GitHub da OCI Pizza",
      force: true,
      waitForState: ["ACTIVE"]
    }' >"${request_file}"

  oci resource-manager configuration-source-provider \
    update-github-access-token-provider \
    --from-json "file://${request_file}"
fi

exit 0
