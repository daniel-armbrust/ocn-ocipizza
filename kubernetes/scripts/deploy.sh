#!/bin/bash

# =============================================================================
# OCI Pizza - Script master de deployment Kubernetes
# =============================================================================
#
# Objetivo:
#   Centralizar e coordenar o deployment dos microsserviços do OCI Pizza
#   nos clusters OKE das regiões GRU (São Paulo) e VCP (Vinhedo).
#
# Funcionamento:
#   1. Recebe a região de destino (gru ou vcp).
#   2. Recebe opcionalmente o nome do microsserviço.
#   3. Valida os parâmetros informados.
#   4. Executa o script de deployment correspondente ao microsserviço.
#   5. Quando nenhum microsserviço é informado, executa todos os serviços
#      habilitados, respeitando a ordem definida neste arquivo.
#
# Responsabilidades dos scripts individuais:
#   - Consultar os outputs regionais do Terraform.
#   - Gerar temporariamente o arquivo configmap.env.
#   - Utilizar o Kustomize para preparar os manifests Kubernetes.
#   - Executar o deployment no cluster OKE correspondente.
#   - Verificar o rollout e remover os arquivos temporários.
#
# Deployment multirregião:
#   O mesmo conjunto de scripts e manifests Kubernetes é reutilizado
#   nas regiões GRU e VCP. Cada região possui seu próprio cluster OKE.
#
# Utilização:
#   ./kubernetes/scripts/deploy.sh gru
#   ./kubernetes/scripts/deploy.sh vcp
#   ./kubernetes/scripts/deploy.sh gru pizza-service
#   ./kubernetes/scripts/deploy.sh vcp pizza-service
#
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# 1. Configurações
# -----------------------------------------------------------------------------

# Obtém a região de destino (gru ou vcp) informada no primeiro argumento.
REGION="${1:-}"

# Obtém o microsserviço informado no segundo argumento.
# Quando omitido, realiza o deployment de todos os serviços habilitados.
SERVICE="${2:-all}"

# Identifica o diretório que contém os scripts de deployment.
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define os microsserviços habilitados para deployment.
# A ordem da lista determina a sequência de execução.
SERVICES=(
    "pizza-service"
    "frontend-service"
)

# -----------------------------------------------------------------------------
# 2. Validação dos parâmetros
# -----------------------------------------------------------------------------

# Aceita somente a região e, opcionalmente, o nome de um microsserviço.
if [[ $# -gt 2 ]]; then
    echo "Uso: $0 <gru|vcp> [all|nome-do-serviço]"
    exit 1
fi

# Valida se a região informada é suportada.
if [[ "$REGION" != "gru" && "$REGION" != "vcp" ]]; then
    echo "Região inválida. Utilize gru ou vcp."
    echo "Uso: $0 <gru|vcp> [all|nome-do-serviço]"
    exit 1
fi

# -----------------------------------------------------------------------------
# 3. Função de deployment
# -----------------------------------------------------------------------------

# Localiza e executa o script individual de deployment do microsserviço.
# A região selecionada é repassada como argumento.
#
# Caso o script não exista ou apresente erro, a execução será interrompida.

deploy_service() {
    local service="$1"
    local script="$SCRIPTS_DIR/deploy-${service}.sh"

    if [[ ! -f "$script" ]]; then
        echo "Script de deployment não encontrado: $script"
        return 1
    fi

    echo "Iniciando deployment do $service na região $REGION."

    bash "$script" "$REGION"

    echo "Deployment do $service concluído."
}

# -----------------------------------------------------------------------------
# 4. Seleção dos microsserviços
# -----------------------------------------------------------------------------

# Se nenhum microsserviço foi informado, executa todos os serviços
# habilitados na lista SERVICES.
if [[ "$SERVICE" == "all" ]]; then

    for service in "${SERVICES[@]}"; do
        deploy_service "$service"
    done

else

    # Verifica se o microsserviço solicitado está habilitado.
    SERVICE_FOUND=false

    for service in "${SERVICES[@]}"; do
        if [[ "$service" == "$SERVICE" ]]; then
            SERVICE_FOUND=true
            break
        fi
    done

    if [[ "$SERVICE_FOUND" != true ]]; then
        echo "Microsserviço não suportado: $SERVICE"
        exit 1
    fi

    # Executa somente o microsserviço solicitado.
    deploy_service "$SERVICE"

fi

# -----------------------------------------------------------------------------
# 5. Finalização
# -----------------------------------------------------------------------------

echo "Processo de deployment finalizado na região $REGION."

exit 0