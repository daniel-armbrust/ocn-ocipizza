#!/usr/bin/env bash

#
# use-oci-env.sh - OCI Pizza
#
# Propósito
# ---------
# Prepara o ambiente do shell para executar os containers da OCI Pizza
# localmente, utilizando recursos reais da Oracle Cloud Infrastructure (OCI).
#
# Este script não faz deployment no OCI e não inicia containers. Ele somente
# carrega e exporta as variáveis que serão herdadas pelo `make` e pelo Docker
# Compose. Dessa forma, os microsserviços continuam sendo executados na
# máquina local, enquanto os providers configurados podem acessar OCI NoSQL,
# OCI Object Storage, OCI Queue e OCI Email Delivery.
#
# Uso recomendado
# ---------------
#
#   ${EDITOR:-vi} .env.oci
#   source ./scripts/use-oci-env.sh
#   make development-oci
#
# O uso de `source` (ou `.`) é obrigatório. Executar `./use-oci-env.sh` cria
# um processo filho e não consegue manter os exports no shell que executará
# o comando `make` em seguida.
#
# Configuração
# ------------
# Os valores podem ser definidos no arquivo `.env.oci`, que é ignorado pelo
# Git, ou exportados previamente no shell. Variáveis exportadas antes do
# `source` têm precedência sobre o arquivo `.env.oci`.
#
# Providers OCI habilitados por padrão:
#   NOSQL_PROVIDER=oci
#   OBJECTSTORAGE_PROVIDER=oci
#   MESSAGING_PROVIDER=oci_queue
#   EMAIL_PROVIDER=oci
#
# Variáveis obrigatórias:
#   NOSQL_COMPARTMENT_ID                 Compartment das tabelas Oracle NoSQL.
#   OCI_QUEUE_ID                         OCID da fila notifications-queue.
#   OCI_EMAIL_DELIVERY_COMPARTMENT_ID    Compartment do OCI Email Delivery.
#                              
# Para autenticação por arquivo, o arquivo do host deve existir em
# OCI_HOST_CONFIG_FILE. Dentro dos containers, o caminho utilizado pelo
# Compose é OCI_CONFIG_FILE=/app/.oci/config.
#
# Segurança
# ---------
# Não coloque chaves privadas, fingerprints, senhas ou OCIDs sensíveis neste
# script. Mantenha esses dados em `.env.oci` ou no arquivo de configuração OCI
# local, ambos fora do controle de versão.
#

set -euo pipefail

# O script foi projetado para ser carregado no shell atual.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo 'Este script deve ser carregado com: source ./scripts/use-oci-env.sh'
    exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OCI_ENV_FILE="${OCI_ENV_FILE:-${PROJECT_ROOT}/.env.oci}"

# Preserva valores exportados antes do source, pois eles têm maior precedência
# do que os valores definidos no arquivo `.env.oci`.
declare -A ENVIRONMENT_OVERRIDES=()

for variable in \
    OCI_REGION OCI_AUTH_MODE OCI_CONFIG_FILE OCI_CONFIG_PROFILE \
    OCI_HOST_CONFIG_FILE NOSQL_PROVIDER NOSQL_COMPARTMENT_ID \
    OBJECTSTORAGE_PROVIDER OBJECTSTORAGE_COMPARTMENT_ID \
    OBJECTSTORAGE_BUCKET MESSAGING_PROVIDER QUEUE_NAME QUEUE_COMPARTMENT_ID \
    OCI_QUEUE_ID EMAIL_PROVIDER OCI_EMAIL_DELIVERY_COMPARTMENT_ID \
    OCI_EMAIL_SENDER_NAME SMTP_EMAIL_SENDER; do
    if [[ -v "${variable}" ]]; then
        ENVIRONMENT_OVERRIDES["${variable}"]="${!variable}"
    fi
done

if [[ -f "${OCI_ENV_FILE}" ]]; then
    echo "Carregando configuração OCI de ${OCI_ENV_FILE}..."
    set -a
    # O arquivo é uma configuração local controlada pelo operador.
    # shellcheck disable=SC1090
    source "${OCI_ENV_FILE}"
    set +a
else
    echo "Arquivo ${OCI_ENV_FILE} não encontrado; usando exports e defaults."
fi

for variable in "${!ENVIRONMENT_OVERRIDES[@]}"; do
    export "${variable}=${ENVIRONMENT_OVERRIDES[${variable}]}"
done

# Defaults para o cenário de homologação local com providers OCI.
export OCI_REGION="${OCI_REGION:-sa-saopaulo-1}"
export OCI_AUTH_MODE="${OCI_AUTH_MODE:-config_file}"
export OCI_CONFIG_PROFILE="${OCI_CONFIG_PROFILE:-DEFAULT}"
export OCI_CONFIG_FILE="${OCI_CONFIG_FILE:-/app/.oci/config}"
export OCI_HOST_CONFIG_FILE="${OCI_HOST_CONFIG_FILE:-${HOME}/.oci/config}"

export NOSQL_PROVIDER="${NOSQL_PROVIDER:-oci}"
export OBJECTSTORAGE_PROVIDER="${OBJECTSTORAGE_PROVIDER:-oci}"
export OBJECTSTORAGE_BUCKET="${OBJECTSTORAGE_BUCKET:-pizza-images}"
export MESSAGING_PROVIDER="${MESSAGING_PROVIDER:-oci_queue}"
export QUEUE_NAME="${QUEUE_NAME:-notifications-queue}"
export EMAIL_PROVIDER="${EMAIL_PROVIDER:-oci}"

required_variables=(
    NOSQL_COMPARTMENT_ID
    OCI_QUEUE_ID
    OCI_EMAIL_DELIVERY_COMPARTMENT_ID
)

for variable in "${required_variables[@]}"; do
    if [[ -z "${!variable:-}" ]]; then
        echo "Erro: ${variable} é obrigatório para o ambiente OCI."
        return 1
    fi
done

case "${OCI_AUTH_MODE}" in
    config_file)
        if [[ ! -f "${OCI_HOST_CONFIG_FILE}" ]]; then
            echo "Erro: arquivo OCI não encontrado: ${OCI_HOST_CONFIG_FILE}"
            return 1
        fi
        ;;
    instance_principal)
        ;;
    *)
        echo "Erro: OCI_AUTH_MODE inválido: ${OCI_AUTH_MODE}"
        echo 'Utilize config_file ou instance_principal.'
        return 1
        ;;
esac

case "${NOSQL_PROVIDER}" in
    oci) ;;
    *)
        echo "Erro: NOSQL_PROVIDER deve ser oci neste ambiente: ${NOSQL_PROVIDER}"
        return 1
        ;;
esac

case "${OBJECTSTORAGE_PROVIDER}" in
    oci) ;;
    *)
        echo "Erro: OBJECTSTORAGE_PROVIDER deve ser oci neste ambiente: ${OBJECTSTORAGE_PROVIDER}"
        return 1
        ;;
esac

case "${MESSAGING_PROVIDER}" in
    oci_queue) ;;
    *)
        echo "Erro: MESSAGING_PROVIDER deve ser oci_queue neste ambiente: ${MESSAGING_PROVIDER}"
        return 1
        ;;
esac

case "${EMAIL_PROVIDER}" in
    oci) ;;
    *)
        echo "Erro: EMAIL_PROVIDER deve ser oci neste ambiente: ${EMAIL_PROVIDER}"
        return 1
        ;;
esac

echo 'Configuração OCI exportada para o shell atual.'
echo "  Região: ${OCI_REGION}"
echo "  Autenticação: ${OCI_AUTH_MODE}"
echo "  NoSQL: ${NOSQL_PROVIDER}"
echo "  Object Storage: ${OBJECTSTORAGE_PROVIDER}"
echo "  Mensageria: ${MESSAGING_PROVIDER} (${QUEUE_NAME})"
echo "  E-mail: ${EMAIL_PROVIDER}"
echo
echo 'Agora execute o comando make desejado no mesmo shell.'
