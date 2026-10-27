#!/bin/bash

# =============================================================================
# OCI Pizza - Deployment Kubernetes do pizza-service
# =============================================================================
#
# Objetivo:
#   Realizar o deployment do pizza-service nos clusters OKE das regiões
#   GRU (São Paulo) ou VCP (Vinhedo), reutilizando os mesmos manifests
#   Kubernetes e o mesmo template de configuração.
#
# Funcionamento:
#   1. Recebe a região de destino (gru ou vcp).
#   2. Consulta os outputs do Terraform para obter os recursos OCI regionais.
#   3. Utiliza o template compartilhado pizza-service.env.template.
#   4. Gera temporariamente um configmap.env com os valores da região.
#   5. Lê o kustomization.yaml do overlay compartilhado através do Kustomize.
#   6. Aplica os manifests no cluster OKE correspondente à região.
#   7. Verifica o Deployment e remove o arquivo temporário.
#
# Integração com Terraform:
#   O Terraform é responsável por provisionar a infraestrutura OCI.
#   Este script apenas consulta os outputs do Terraform State existente.
#   Nenhum comando terraform apply é executado.
#
# Deployment multirregião:
#   Os manifests Kubernetes são compartilhados entre GRU e VCP.
#   A região determina quais outputs Terraform e qual contexto OKE utilizar.
#   Cada região possui seu próprio cluster Kubernetes.
#
# ConfigMap:
#   O arquivo configmap.env é gerado durante a execução e não deve ser
#   versionado no Git. O arquivo é removido ao finalizar o script,
#   inclusive quando ocorrer um erro.
#
#   Como o overlay é compartilhado, um bloqueio impede deployments
#   simultâneos que poderiam misturar configurações regionais.
#
# Pré-requisitos:
#   - Terraform inicializado e infraestrutura previamente provisionada.
#   - Outputs Terraform disponíveis no Root Module.
#   - kubectl configurado com os contextos oke-gru e oke-vcp.
#   - Comandos terraform, kubectl, jq, envsubst e flock instalados.
#   - Imagem Docker do pizza-service disponível no OCIR.
#   - ServiceAccount e permissões OCI previamente configurados.
#
# Utilização:
#   ./kubernetes/scripts/deploy-pizza-service.sh gru
#   ./kubernetes/scripts/deploy-pizza-service.sh vcp
#
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# 1. Configurações e diretórios
# -----------------------------------------------------------------------------

SERVICE="pizza-service"

# Obtém a região de destino (gru ou vcp) informada no primeiro argumento 
# do script.
REGION="${1:-}"

# Define o namespace Kubernetes utilizado pelos microsserviços do 
# OCI Pizza.
NAMESPACE="oci-pizza"

# Identifica o diretório kubernetes/ a partir da localização deste 
# script.
KUBERNETES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Identifica a raiz do repositório OCI Pizza.
PROJECT_DIR="$(cd "$KUBERNETES_DIR/.." && pwd)"

# Define o diretório Terraform utilizado para consultar os outputs da 
# infraestrutura OCI.
TERRAFORM_DIR="$PROJECT_DIR/terraform"

# Localiza o template compartilhado de variáveis de ambiente do 
# microsserviço.
TEMPLATE_FILE="$KUBERNETES_DIR/configmaps/$SERVICE.env.template"

# Define o diretório do overlay Kustomize compartilhado entre 
# GRU e VCP.
OVERLAY_DIR="$KUBERNETES_DIR/overlays/$SERVICE"

# Define o arquivo temporário de configuração gerado para o 
# deployment.
CONFIG_FILE="$OVERLAY_DIR/configmap.env"

# Localiza o manifesto Kubernetes responsável pela criação do 
# namespace.
NAMESPACE_FILE="$KUBERNETES_DIR/base/namespace.yaml"

# -----------------------------------------------------------------------------
# 2. Validação da região
# -----------------------------------------------------------------------------

if [[ "$REGION" != "gru" && "$REGION" != "vcp" ]]; then
    echo "Uso: $0 <gru|vcp>"
    exit 1
fi

# Cada região utiliza seu próprio contexto Kubernetes.
KUBE_CONTEXT="oke-$REGION"

echo "Iniciando deployment do $SERVICE na região $REGION."

# -----------------------------------------------------------------------------
# 3. Validação dos pré-requisitos
# -----------------------------------------------------------------------------

for cmd in terraform kubectl jq envsubst flock; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Comando obrigatório não encontrado: $cmd"
        exit 1
    fi
done

if [[ ! -f "$TEMPLATE_FILE" ]]; then
    echo "Template não encontrado: $TEMPLATE_FILE"
    exit 1
fi

if [[ ! -f "$OVERLAY_DIR/kustomization.yaml" ]]; then
    echo "Arquivo kustomization.yaml não encontrado: $OVERLAY_DIR"
    exit 1
fi

if [[ ! -f "$NAMESPACE_FILE" ]]; then
    echo "Arquivo namespace.yaml não encontrado: $NAMESPACE_FILE"
    exit 1
fi

if ! kubectl config get-contexts -o name | grep -Fxq "$KUBE_CONTEXT"; then
    echo "Contexto Kubernetes não encontrado: $KUBE_CONTEXT"
    exit 1
fi

# -----------------------------------------------------------------------------
# 4. Bloqueio de deployments simultâneos
# -----------------------------------------------------------------------------

# Como GRU e VCP utilizam o mesmo overlay, somente uma execução pode
# gerar e utilizar o configmap.env por vez.
#
# O flock mantém o bloqueio até o término do processo.
# O arquivo de lock permanece disponível para futuras execuções.

LOCK_FILE="$OVERLAY_DIR/.deploy.lock"

exec 9>"$LOCK_FILE"

if ! flock -n 9; then
    echo "Já existe um deployment utilizando o overlay do $SERVICE."
    exit 1
fi

# Impede sobrescrever um configmap.env preexistente.
if [[ -e "$CONFIG_FILE" ]]; then
    echo "Arquivo temporário já existente: $CONFIG_FILE"
    echo "Verifique e remova o arquivo antes de executar novamente."
    exit 1
fi

# Remove o arquivo gerado quando o processo terminar.
cleanup() {
    rm -f "$CONFIG_FILE"
}

trap cleanup EXIT

# -----------------------------------------------------------------------------
# 5. Consulta aos outputs Terraform
# -----------------------------------------------------------------------------

# Consulta o Terraform State existente sem modificar a infraestrutura.
#
# A função recebe o nome de um output que contém um mapa por região,
# por exemplo:
#
#   nosql_table_names = {
#     gru = "pizzas"
#     vcp = "pizzas"
#   }

get_region_output() {
    local output_name="$1"

    terraform -chdir="$TERRAFORM_DIR" \
        output -json "$output_name" |
        jq -er --arg region "$REGION" \
            '.[$region] | select(type == "string" and length > 0)'
}

# Consulta um output Terraform que contém somente uma string.
get_output() {
    local output_name="$1"

    terraform -chdir="$TERRAFORM_DIR" \
        output -raw "$output_name"
}

# Obtém o OCID do log-pizza-service na região selecionada.
#
# O output log_ids do Terraform contém os OCIDs dos logs
# dos microsserviços organizados por região e nome do recurso.
#
# Estrutura esperada:
#
#   gru:
#     log-pizza-service: <OCID>
#   vcp:
#     log-pizza-service: <OCID>
#
# O output deve estar disponível no Root Module do Terraform.

get_logging_id() {
    terraform -chdir="$TERRAFORM_DIR" \
        output -json log_ids |
        jq -er \
            --arg region "$REGION" \
            --arg log_name "log-$SERVICE" \
            '.[$region][$log_name] | select(type == "string" and length > 0)'
}

echo "Consultando outputs Terraform."

NOSQL_TABLE_NAME="$(get_region_output nosql_table_names)"
NOSQL_COMPARTMENT_ID="$(get_output compartment_id)"
OBJECTSTORAGE_BUCKET="$(get_region_output objectstorage_bucket_names)"
OCI_LOG_ID="$(get_logging_id)"

# Interrompe o deployment caso algum valor obrigatório esteja ausente.
for variable in \
    NOSQL_TABLE_NAME \
    NOSQL_COMPARTMENT_ID \
    OBJECTSTORAGE_BUCKET \
    OCI_LOG_ID; do

    if [[ -z "${!variable}" || "${!variable}" == "null" ]]; then
        echo "Variável obrigatória não definida: $variable"
        exit 1
    fi
done

export NOSQL_TABLE_NAME
export NOSQL_COMPARTMENT_ID
export OBJECTSTORAGE_BUCKET
export OCI_LOG_ID

# -----------------------------------------------------------------------------
# 6. Geração temporária do ConfigMap
# -----------------------------------------------------------------------------

# O template compartilhado contém configurações fixas da aplicação e
# placeholders das informações obtidas do Terraform.
#
# O envsubst substitui somente as variáveis indicadas.
#
# O arquivo final configmap.env será utilizado pelo configMapGenerator
# definido no kustomization.yaml do overlay compartilhado.
#
# Esse arquivo não será versionado e será excluído após o deployment.

echo "Gerando configuração temporária do $SERVICE."

umask 077

TEMP_FILE="$(mktemp "$OVERLAY_DIR/.configmap.XXXXXX")"

# Garante também a remoção do arquivo intermediário.
cleanup() {
    rm -f "$TEMP_FILE" "$CONFIG_FILE"
}

trap cleanup EXIT

envsubst \
    '${NOSQL_TABLE_NAME} ${NOSQL_COMPARTMENT_ID} ${OBJECTSTORAGE_BUCKET} ${OCI_LOG_ID}' \
    < "$TEMPLATE_FILE" > "$TEMP_FILE"

# Impede que placeholders conhecidos permaneçam sem substituição.
if grep -Eq \
    '\$\{(NOSQL_TABLE_NAME|NOSQL_COMPARTMENT_ID|OBJECTSTORAGE_BUCKET|OCI_LOG_ID)\}' \
    "$TEMP_FILE"; then

    echo "O arquivo de configuração contém variáveis não resolvidas."
    exit 1
fi

mv "$TEMP_FILE" "$CONFIG_FILE"

echo "Configuração regional preparada."

# -----------------------------------------------------------------------------
# 7. Validação da conexão com o cluster OKE
# -----------------------------------------------------------------------------

echo "Verificando conexão com o cluster $KUBE_CONTEXT."

kubectl --context "$KUBE_CONTEXT" get --raw=/version > /dev/null

# -----------------------------------------------------------------------------
# 8. Preparação do namespace
# -----------------------------------------------------------------------------

# O namespace é compartilhado pelos microsserviços do OCI Pizza,
# mas existe independentemente em cada cluster regional.

echo "Verificando namespace $NAMESPACE."

kubectl --context "$KUBE_CONTEXT" \
    apply -f "$NAMESPACE_FILE"

# -----------------------------------------------------------------------------
# 9. Renderização dos manifests com Kustomize
# -----------------------------------------------------------------------------

# O Kustomize lê o arquivo:
#
#   kubernetes/overlays/pizza-service/kustomization.yaml
#
# Esse arquivo referencia os recursos Kubernetes compartilhados da base:
#
#   kubernetes/base/pizza-service/
#
# Também utiliza o configmap.env temporário para gerar o ConfigMap.
#
# A renderização permite identificar problemas estruturais antes de aplicar
# os recursos no cluster.

echo "Validando manifests Kubernetes."

kubectl kustomize "$OVERLAY_DIR" > /dev/null

# -----------------------------------------------------------------------------
# 10. Deployment no OKE
# -----------------------------------------------------------------------------

# Aplica os recursos renderizados pelo Kustomize no contexto selecionado.
#
# O mesmo overlay pode ser utilizado em GRU ou VCP porque as informações
# regionais foram resolvidas anteriormente pelo Terraform.

echo "Aplicando manifests no cluster $KUBE_CONTEXT."

kubectl --context "$KUBE_CONTEXT" apply -k "$OVERLAY_DIR"

# -----------------------------------------------------------------------------
# 11. Verificação do Deployment
# -----------------------------------------------------------------------------

# Aguarda a disponibilização do Deployment.
# Em caso de timeout ou erro, o script retorna código diferente de zero.

echo "Verificando disponibilização do $SERVICE."

kubectl --context "$KUBE_CONTEXT" \
    -n "$NAMESPACE" \
    rollout status "deployment/$SERVICE" \
    --timeout=180s

echo "Deployment do $SERVICE concluído na região $REGION."

exit 0