#!/usr/bin/env bash

# Cria os namespaces do laboratório e aplica todos os Pods do diretório
# kubernetes/pods. Os parâmetros têm precedência sobre as variáveis de ambiente.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PODS_DIR="${SCRIPT_DIR}/../kubernetes/pods"
NAMESPACES_DIR="${SCRIPT_DIR}/../kubernetes/namespaces"

# Usa os valores do ambiente quando os parâmetros correspondentes não forem
# informados na linha de comando.
registry="${REGISTRY:-}"
oci_namespace="${OCI_NAMESPACE:-}"

# Mantém os grupos explícitos para garantir que toda a infraestrutura seja
# criada antes dos microsserviços que dependem dela.
infrastructure_manifests=(
  "$PODS_DIR/pod-redis.yaml"
  "$PODS_DIR/pod-nosql.yaml"
  "$PODS_DIR/pod-objectstorage.yaml"
  "$PODS_DIR/pod-mysql.yaml"
  "$PODS_DIR/pod-rabbitmq.yaml"
  "$PODS_DIR/pod-mailpit.yaml"
)

service_manifests=(
  "$PODS_DIR/pod-admin-service.yaml"
  "$PODS_DIR/pod-delivery-service.yaml"
  "$PODS_DIR/pod-frontend-service.yaml"
  "$PODS_DIR/pod-notification-service.yaml"
  "$PODS_DIR/pod-order-service.yaml"
  "$PODS_DIR/pod-pizza-service.yaml"
  "$PODS_DIR/pod-user-service.yaml"
)

# Exibe as opções aceitas pelo script e as variáveis de ambiente equivalentes.
usage() {
  cat <<'EOF'
Uso: ./scripts/pods-deploy.sh [opções]

Opções:
  --registry <registry>          Registry das imagens, por exemplo gru.ocir.io.
  --oci-namespace <namespace>   Namespace da tenancy retornado por oci os ns get.
  -h, --help                    Exibe esta ajuda.

Os valores também podem ser definidos pelas variáveis de ambiente REGISTRY e
OCI_NAMESPACE. Os parâmetros informados na linha de comando têm precedência.
EOF
}

# Processa com envsubst e aplica, na ordem recebida, um grupo de manifests no
# cluster Kubernetes configurado no contexto atual do kubectl.
deploy_manifests() {
  local group_name="$1"
  local manifest
  shift

  echo "Aplicando Pods de ${group_name}..."

  # Limita a substituição às duas variáveis conhecidas para preservar qualquer
  # outro caractere '$' que possa existir futuramente nos manifests.
  for manifest in "$@"; do
    echo "Aplicando $(basename "$manifest")..."

    envsubst '${REGISTRY} ${OCI_NAMESPACE}' <"$manifest" | kubectl apply -f -
  done
}

while (($# > 0)); do
  case "$1" in
    --registry)
      [[ $# -ge 2 ]] || { echo "Erro: --registry requer um valor." >&2; exit 1; }
      registry="$2"
      shift 2
      ;;

    --oci-namespace)
      [[ $# -ge 2 ]] || { echo "Erro: --oci-namespace requer um valor." >&2; exit 1; }
      oci_namespace="$2"
      shift 2
      ;;

    -h | --help)
      usage
      exit 0
      ;;

    *)
      echo "Erro: parâmetro desconhecido: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

# Interrompe antes de acessar o cluster quando alguma configuração obrigatória
# não tiver sido fornecida.
[[ -n "$registry" ]] || {
  echo "Erro: informe REGISTRY ou --registry." >&2; exit 1;
}

[[ -n "$oci_namespace" ]] || {
  echo "Erro: informe OCI_NAMESPACE ou --oci-namespace." >&2; exit 1;
}

for command in envsubst kubectl; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "Erro: o comando '$command' não está instalado ou não está no PATH." >&2
    exit 1
  }
done

# Remove barras finais para evitar caminhos de imagem com barras duplicadas.
export REGISTRY="${registry%/}"
export OCI_NAMESPACE="${oci_namespace%/}"

# Os namespaces precisam existir antes da criação dos Pods que os referenciam.
kubectl apply -f "$NAMESPACES_DIR"

deploy_manifests "infraestrutura" "${infrastructure_manifests[@]}"
deploy_manifests "serviços" "${service_manifests[@]}"

exit 0
