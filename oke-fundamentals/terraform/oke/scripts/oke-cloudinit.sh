#!/bin/bash

#
# oke-fundamentals/terraform/oke/scripts/oke-cloudinit.sh
#
# Inicializa um worker node gerenciado pelo OKE preservando o script padrão
# de inicialização do serviço Kubernetes Engine e reservando recursos para
# os daemons do Kubernetes.
#
# Este arquivo deve ser fornecido como user_data no node pool. O script padrão
# do OKE é obrigatório para que o worker node consiga ingressar no cluster.
#
# https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengtroubleshooting_topic-node_issues.htm
#

set -euo pipefail

# Variáveis globais

# Recursos reservados para os daemons do Kubernetes. Quando vazios, os valores
# são calculados pela função calculate_reserved_resources.
KUBE_RESERVED_CPU="${KUBE_RESERVED_CPU:-}"
KUBE_RESERVED_MEMORY="${KUBE_RESERVED_MEMORY:-}"

# Reservas recomendadas pela Oracle para os daemons do sistema operacional.
SYSTEM_RESERVED_CPU="${SYSTEM_RESERVED_CPU:-100m}"
SYSTEM_RESERVED_MEMORY="${SYSTEM_RESERVED_MEMORY:-100Mi}"

# Funções

# Calcula as reservas recomendadas pela Oracle com base nos recursos do host.
# Valores já preenchidos no ambiente têm precedência sobre o cálculo.
calculate_reserved_resources() {
  local cpu_cores
  local memory_kib
  local memory_gib
  local extra_cpu_millicores
  local extra_memory_mib

  cpu_cores="$(nproc 2>/dev/null || getconf _NPROCESSORS_ONLN)"
  memory_kib="$(awk '/^MemTotal:/ {print $2; exit}' /proc/meminfo)"

  if [[ -z "$cpu_cores" || "$cpu_cores" -lt 1 ]]; then
    echo "Erro: não foi possível determinar a quantidade de CPUs do worker node." >&2
    exit 1
  fi

  if [[ -z "$memory_kib" || "$memory_kib" -lt 1 ]]; then
    echo "Erro: não foi possível determinar a memória do worker node." >&2
    exit 1
  fi

  if [[ -z "$KUBE_RESERVED_CPU" ]]; then
    case "$cpu_cores" in
      1) KUBE_RESERVED_CPU="60m" ;;
      2) KUBE_RESERVED_CPU="70m" ;;
      3) KUBE_RESERVED_CPU="80m" ;;
      4) KUBE_RESERVED_CPU="85m" ;;
      5) KUBE_RESERVED_CPU="90m" ;;
      *)
        extra_cpu_millicores=$((90 + ((cpu_cores - 5) * 5 + 1) / 2))
        KUBE_RESERVED_CPU="${extra_cpu_millicores}m"
        ;;
    esac
  fi

  if [[ -z "$KUBE_RESERVED_MEMORY" ]]; then
    # Arredonda a memória para cima antes de aplicar as faixas recomendadas.
    memory_gib=$(( (memory_kib + 1024 * 1024 - 1) / (1024 * 1024) ))
    if (( memory_gib <= 8 )); then
      KUBE_RESERVED_MEMORY="1Gi"
    elif (( memory_gib <= 16 )); then
      KUBE_RESERVED_MEMORY="2Gi"
    elif (( memory_gib <= 128 )); then
      KUBE_RESERVED_MEMORY="9Gi"
    else
      extra_memory_mib=$(( (memory_gib - 128) * 20 ))
      KUBE_RESERVED_MEMORY="$((9 * 1024 + extra_memory_mib))Mi"
    fi
  fi
}

# Desabilita o plugin Cloud Guard Workload Protection.
disable_cloud_guard_workload_protection() {
  local agent_config_file="/etc/oracle-cloud-agent/agent.yml"
  local agent_service="oracle-cloud-agent.service"

  if [[ ! -f "$agent_config_file" ]]; then
    echo "Arquivo ${agent_config_file} não encontrado; plugin oci-wlp não alterado."
    return 0
  fi

  sed -i \
    '/^  oci-wlp:/,/^  oci-blockautoconfig:/{/^  oci-blockautoconfig:/! s/^\(    disabled:\)[[:space:]]*false/\1 true/;}' \
    "$agent_config_file"

  if systemctl restart "$agent_service"; then
    echo "Plugin oci-wlp desabilitado e Oracle Cloud Agent reiniciado."
  else
    echo "Aviso: não foi possível reiniciar o ${agent_service}." >&2
  fi
}

# Fluxo principal

calculate_reserved_resources

# Baixa e executa o script padrão do OKE. Não remova nem altere esta etapa.
curl --fail \
  -H "Authorization: Bearer Oracle" \
  -L0 \
  http://169.254.169.254/opc/v2/instance/metadata/oke_init_script \
  | base64 --decode > /var/run/oke-init.sh

# Reserva recursos para os daemons do Kubernetes e do sistema operacional
# conforme a recomendação da Oracle. Os valores podem ser sobrescritos pelas
# variáveis globais acima.
bash /var/run/oke-init.sh \
  --kubelet-extra-args \
  "--kube-reserved=cpu=${KUBE_RESERVED_CPU},memory=${KUBE_RESERVED_MEMORY} \
--system-reserved=cpu=${SYSTEM_RESERVED_CPU},memory=${SYSTEM_RESERVED_MEMORY}"

# Aplica a configuração do plugin depois que o bootstrap padrão do OKE termina.
disable_cloud_guard_workload_protection

exit 0
