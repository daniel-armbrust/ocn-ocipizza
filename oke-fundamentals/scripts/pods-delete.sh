#!/usr/bin/env bash

# Exclui os Pods do laboratório e, depois, os namespaces definidos nos
# manifests. Os parâmetros têm precedência sobre as variáveis de ambiente.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PODS_DIR="${SCRIPT_DIR}/../kubernetes/pods"
NAMESPACES_DIR="${SCRIPT_DIR}/../kubernetes/namespaces"

# Usa os valores do ambiente quando os parâmetros correspondentes não forem
# informados na linha de comando.
registry="${REGISTRY:-}"
oci_namespace="${OCI_NAMESPACE:-}"

# Exibe as opções aceitas pelo script e as variáveis de ambiente equivalentes.
usage() {
  cat <<'EOF'
Uso: ./scripts/pods-delete.sh [opções]

Opções:
  --registry <registry>          Registry das imagens, por exemplo gru.ocir.io.
  --oci-namespace <namespace>   Namespace da tenancy retornado por oci os ns get.
  -h, --help                    Exibe esta ajuda.

Os valores também podem ser definidos pelas variáveis de ambiente REGISTRY e
OCI_NAMESPACE. Os parâmetros informados na linha de comando têm precedência.
EOF
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

# Os manifests precisam receber os mesmos valores usados no deploy antes de
# serem enviados ao kubectl para exclusão.
[[ -n "$registry" ]] || { echo "Erro: informe REGISTRY ou --registry." >&2; exit 1; }
[[ -n "$oci_namespace" ]] || { echo "Erro: informe OCI_NAMESPACE ou --oci-namespace." >&2; exit 1; }

for command in envsubst kubectl; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "Erro: o comando '$command' não está instalado ou não está no PATH." >&2
    exit 1
  }
done

# Remove barras finais para manter as referências das imagens normalizadas.
export REGISTRY="${registry%/}"
export OCI_NAMESPACE="${oci_namespace%/}"

# Exclui os Pods antes dos namespaces para tornar explícita a ordem inversa do
# deploy. Recursos que já não existirem não interrompem a limpeza.
for manifest in "$PODS_DIR"/pod-*.yaml; do
  echo "Excluindo $(basename "$manifest")..."

  envsubst '${REGISTRY} ${OCI_NAMESPACE}' <"$manifest" \
    | kubectl delete --ignore-not-found=true -f -
done

# A exclusão de um namespace também remove qualquer recurso remanescente nele.
kubectl delete --ignore-not-found=true -f "$NAMESPACES_DIR"

exit 0
