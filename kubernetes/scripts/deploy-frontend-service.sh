#!/bin/bash

# =============================================================================
# OCI Pizza - Deployment Kubernetes do frontend-service
# =============================================================================
#
# Objetivo:
#   Realizar o deployment do frontend-service nos clusters OKE das regiões
#   GRU (São Paulo) e VCP (Vinhedo), reutilizando os mesmos manifests
#   Kubernetes e o mesmo template de configuração.
#
# Funcionamento:
#   1. Recebe a região de destino (gru ou vcp).
#   2. Consulta os outputs do Terraform para obter os recursos OCI regionais.
#   3. Obtém o OCID do log-frontend-service e o endpoint do OCI Cache.
#   4. Gera temporariamente o configmap.env a partir do template compartilhado.
#   5. Verifica o Kubernetes Secret utilizado pelo frontend-service.
#   6. Lê o kustomization.yaml do overlay compartilhado através do Kustomize.
#   7. Aplica os manifests no cluster OKE correspondente à região.
#   8. Verifica o Deployment e remove os arquivos temporários.
#
# Integração com Terraform:
#   O Terraform provisiona os recursos OCI necessários ao frontend-service.
#   Este script consulta somente os outputs do Terraform State existente,
#   sem executar terraform plan ou terraform apply.
#
# Deployment multirregião:
#   Os clusters OKE de GRU e VCP utilizam os mesmos manifests Kubernetes.
#   A região selecionada determina os outputs Terraform e o contexto OKE.
#
# ConfigMap:
#   O arquivo configmap.env é gerado temporariamente a partir de
#   kubernetes/configmaps/frontend-service.env.template.
#
#   O arquivo gerado não deve ser versionado no Git e será removido
#   automaticamente ao término da execução.
#
# Secrets:
#   SESSION_SECRET_KEY e CSRF_SECRET_KEY são fornecidos pelo Kubernetes
#   Secret frontend-service-secret, previamente criado no cluster.
#
#   O script valida sua existência, mas não cria nem exibe seus valores.
#
# Concorrência:
#   Como o overlay é compartilhado, o flock impede que deployments
#   simultâneos utilizem o mesmo configmap.env.
#
# Pré-requisitos:
#   - Infraestrutura OCI previamente provisionada pelo Terraform.
#   - Outputs Terraform disponíveis no Root Module.
#   - Contextos Kubernetes oke-gru e oke-vcp configurados.
#   - Comandos terraform, kubectl, jq, envsubst e flock instalados.
#   - Imagem Docker do frontend-service disponível no OCIR.
#   - Secret frontend-service-secret previamente criado no cluster.
#
# Utilização:
#   ./kubernetes/scripts/deploy-frontend-service.sh gru
#   ./kubernetes/scripts/deploy-frontend-service.sh vcp
#
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# 1. Configurações e diretórios
# -----------------------------------------------------------------------------

# Obtém a região informada no primeiro argumento do script.
REGION="${1:-}"

# Define o microsserviço responsável por este deployment.
SERVICE="frontend-service"

# Define o namespace Kubernetes utilizado pelos microsserviços.
NAMESPACE="oci-pizza"

# Identifica o diretório kubernetes/ a partir da localização deste script.
KUBERNETES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Identifica a raiz do repositório OCI Pizza.
PROJECT_DIR="$(cd "$KUBERNETES_DIR/.." && pwd)"

# Define o diretório Terraform utilizado para consultar os outputs OCI.
TERRAFORM_DIR="$PROJECT_DIR/terraform"

# Localiza o template compartilhado de configuração do frontend-service.
TEMPLATE_FILE="$KUBERNETES_DIR/configmaps/$SERVICE.env.template"

# Define o overlay Kustomize compartilhado entre as regiões GRU e VCP.
OVERLAY_DIR="$KUBERNETES_DIR/overlays/$SERVICE"

# Define o arquivo temporário utilizado para gerar o ConfigMap Kubernetes.
CONFIG_FILE="$OVERLAY_DIR/configmap.env"

# Localiza o manifesto Kubernetes responsável pela criação do namespace.
NAMESPACE_FILE="$KUBERNETES_DIR/base/namespace.yaml"

# Define o Secret que contém as chaves de sessão e proteção CSRF.
SECRET_NAME="frontend-service-secret"

# -----------------------------------------------------------------------------
# 2. Validação da região
# -----------------------------------------------------------------------------

# Valida a quantidade de argumentos e a região de destino.
if [[ $# -ne 1 || ( "$REGION" != "gru" && "$REGION" != "vcp" ) ]]; then
    echo "Uso: $0 <gru|vcp>"
    exit 1
fi

# Seleciona o contexto Kubernetes correspondente à região.
KUBE_CONTEXT="oke-$REGION"

echo "Iniciando deployment do $SERVICE na região $REGION."

# -----------------------------------------------------------------------------
# 3. Validação dos pré-requisitos
# -----------------------------------------------------------------------------

# Verifica se os comandos necessários estão instalados.
for cmd in terraform kubectl jq envsubst flock mktemp; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Comando obrigatório não encontrado: $cmd"
        exit 1
    fi
done

# Verifica a existência do template de configuração.
if [[ ! -f "$TEMPLATE_FILE" ]]; then
    echo "Template não encontrado: $TEMPLATE_FILE"
    exit 1
fi

# Verifica a existência do arquivo Kustomize do overlay compartilhado.
if [[ ! -f "$OVERLAY_DIR/kustomization.yaml" ]]; then
    echo "Arquivo kustomization.yaml não encontrado: $OVERLAY_DIR"
    exit 1
fi

# Verifica a existência do manifesto do namespace Kubernetes.
if [[ ! -f "$NAMESPACE_FILE" ]]; then
    echo "Arquivo namespace.yaml não encontrado: $NAMESPACE_FILE"
    exit 1
fi

# Verifica se o contexto Kubernetes da região está configurado.
if ! kubectl config get-contexts -o name | grep -Fxq "$KUBE_CONTEXT"; then
    echo "Contexto Kubernetes não encontrado: $KUBE_CONTEXT"
    exit 1
fi

# -----------------------------------------------------------------------------
# 4. Bloqueio de deployments simultâneos
# -----------------------------------------------------------------------------

# Impede que deployments de GRU e VCP utilizem simultaneamente
# o mesmo arquivo configmap.env do overlay compartilhado.
LOCK_FILE="$OVERLAY_DIR/.deploy.lock"

exec 9>"$LOCK_FILE"

if ! flock -n 9; then
    echo "Já existe um deployment utilizando o overlay do $SERVICE."
    exit 1
fi

# Não sobrescreve um arquivo de configuração existente.
if [[ -e "$CONFIG_FILE" ]]; then
    echo "Arquivo temporário já existente: $CONFIG_FILE"
    echo "Verifique sua origem antes de removê-lo."
    exit 1
fi

# Define a função responsável por remover os arquivos temporários.
TEMP_FILE=""

cleanup() {
    if [[ -n "$TEMP_FILE" ]]; then
        rm -f "$TEMP_FILE"
    fi

    rm -f "$CONFIG_FILE"
}

# Executa a limpeza ao finalizar o script, inclusive em caso de erro.
trap cleanup EXIT

# -----------------------------------------------------------------------------
# 5. Consulta aos outputs Terraform
# -----------------------------------------------------------------------------

# Obtém um output Terraform organizado por região.
#
# Estrutura esperada:
#
#   gru: <VALOR>
#   vcp: <VALOR>
#
# A função consulta o Terraform State sem modificar a infraestrutura.
get_region_output() {
    local output_name="$1"

    terraform -chdir="$TERRAFORM_DIR" \
        output -json "$output_name" |
        jq -er --arg region "$REGION" \
            '.[$region] | select(type == "string" and length > 0)'
}

# Obtém o OCID do log específico do frontend-service.
#
# O output log_ids contém os OCIDs organizados por região e nome do log.
#
# Estrutura esperada:
#
#   gru:
#     log-frontend-service: <OCID>
#   vcp:
#     log-frontend-service: <OCID>
get_logging_id() {
    terraform -chdir="$TERRAFORM_DIR" \
        output -json log_ids |
        jq -er \
            --arg region "$REGION" \
            --arg log_name "log-$SERVICE" \
            '.[$region][$log_name] | select(type == "string" and length > 0)'
}

echo "Consultando outputs Terraform."

# Obtém o OCID regional do log-frontend-service.
OCI_LOG_ID="$(get_logging_id)"

# Obtém o FQDN do endpoint primário do OCI Cache na região selecionada.
# O output redis_endpoints deve utilizar primary_fqdn do módulo Terraform.
REDIS_ENDPOINT="$(get_region_output redis_endpoints)"

# Valida os valores obrigatórios obtidos do Terraform.
for variable in OCI_LOG_ID REDIS_ENDPOINT; do
    if [[ -z "${!variable}" || "${!variable}" == "null" ]]; then
        echo "Variável obrigatória não definida: $variable"
        exit 1
    fi
done

# Disponibiliza as variáveis regionais para substituição no template.
export OCI_LOG_ID
export REDIS_ENDPOINT

# -----------------------------------------------------------------------------
# 6. Geração temporária do ConfigMap
# -----------------------------------------------------------------------------

# Utiliza o template compartilhado:
#
#   kubernetes/configmaps/frontend-service.env.template
#
# As variáveis OCI_LOG_ID e REDIS_ENDPOINT serão substituídas pelos
# valores obtidos do Terraform.
#
# A variável PERSISTENCE_PROVIDER=redis permanece definida no template.
#
# O arquivo resultante configmap.env será utilizado pelo configMapGenerator
# do overlay e não será armazenado permanentemente no repositório.

echo "Gerando configuração temporária do $SERVICE."

# Restringe as permissões dos arquivos temporários criados pelo script.
umask 077

# Cria um arquivo intermediário no próprio diretório do overlay.
TEMP_FILE="$(mktemp "$OVERLAY_DIR/.configmap.XXXXXX")"

# Substitui somente as variáveis regionais declaradas no template.
envsubst '${OCI_LOG_ID} ${REDIS_ENDPOINT}' \
    < "$TEMPLATE_FILE" > "$TEMP_FILE"

# Verifica se algum placeholder permaneceu sem substituição.
if grep -Eq '\$\{[A-Za-z_][A-Za-z0-9_]*\}' "$TEMP_FILE"; then
    echo "O arquivo de configuração contém variáveis não resolvidas."
    exit 1
fi

# Disponibiliza o arquivo final para utilização pelo Kustomize.
mv "$TEMP_FILE" "$CONFIG_FILE"
TEMP_FILE=""

echo "Configuração regional preparada."

# -----------------------------------------------------------------------------
# 7. Validação da conexão com o cluster OKE
# -----------------------------------------------------------------------------

# Verifica se o cluster da região selecionada está acessível.
echo "Verificando conexão com o cluster $KUBE_CONTEXT."

kubectl --context "$KUBE_CONTEXT" get --raw=/version > /dev/null

# -----------------------------------------------------------------------------
# 8. Preparação do namespace
# -----------------------------------------------------------------------------

# O namespace oci-pizza é criado ou atualizado no cluster regional.
# GRU e VCP possuem namespaces independentes, embora compartilhem o nome.
echo "Verificando namespace $NAMESPACE."

kubectl --context "$KUBE_CONTEXT" apply -f "$NAMESPACE_FILE"

# -----------------------------------------------------------------------------
# 9. Validação do Kubernetes Secret
# -----------------------------------------------------------------------------

# O frontend-service utiliza duas chaves sensíveis:
#
#   SESSION_SECRET_KEY
#   CSRF_SECRET_KEY
#
# Essas chaves devem existir no Secret frontend-service-secret,
# previamente provisionado no namespace oci-pizza.
#
# O script verifica somente a existência das chaves, sem imprimir
# seus valores.

echo "Verificando Kubernetes Secret $SECRET_NAME."

if ! kubectl --context "$KUBE_CONTEXT" \
    -n "$NAMESPACE" \
    get secret "$SECRET_NAME" > /dev/null 2>&1; then

    echo "Kubernetes Secret não encontrado: $SECRET_NAME"
    exit 1
fi

# Obtém apenas os nomes das chaves existentes no Secret.
# Nenhum valor sensível é exibido.
SECRET_KEYS="$(
    kubectl --context "$KUBE_CONTEXT" \
        -n "$NAMESPACE" \
        get secret "$SECRET_NAME" -o json |
        jq -r '.data | keys[]'
)"

# Confirma que as duas chaves obrigatórias estão presentes.
for secret_key in SESSION_SECRET_KEY CSRF_SECRET_KEY; do
    if ! grep -Fxq "$secret_key" <<< "$SECRET_KEYS"; then
        echo "Chave obrigatória não encontrada no Secret: $secret_key"
        exit 1
    fi
done

echo "Kubernetes Secret validado."

# -----------------------------------------------------------------------------
# 10. Renderização dos manifests com Kustomize
# -----------------------------------------------------------------------------

# O Kustomize utiliza o arquivo:
#
#   kubernetes/overlays/frontend-service/kustomization.yaml
#
# Esse arquivo referencia:
#
#   kubernetes/base/frontend-service/
#
# E utiliza o configmap.env temporário para gerar o ConfigMap.
#
# A renderização permite identificar erros estruturais antes de
# aplicar os manifests no cluster.

echo "Validando manifests Kubernetes."

kubectl kustomize "$OVERLAY_DIR" > /dev/null

# -----------------------------------------------------------------------------
# 11. Deployment no OKE
# -----------------------------------------------------------------------------

# Aplica os recursos Kubernetes no cluster regional selecionado.
# Os mesmos manifests são utilizados em GRU e VCP.

echo "Aplicando manifests no cluster $KUBE_CONTEXT."

kubectl --context "$KUBE_CONTEXT" apply -k "$OVERLAY_DIR"

# -----------------------------------------------------------------------------
# 12. Verificação do Deployment
# -----------------------------------------------------------------------------

# Aguarda a disponibilização do frontend-service no cluster OKE.
# Uma falha ou timeout interrompe o script com código diferente de zero.

echo "Verificando disponibilização do $SERVICE."

kubectl --context "$KUBE_CONTEXT" \
    -n "$NAMESPACE" \
    rollout status "deployment/$SERVICE" \
    --timeout=180s

echo "Deployment do $SERVICE concluído na região $REGION."

exit 0