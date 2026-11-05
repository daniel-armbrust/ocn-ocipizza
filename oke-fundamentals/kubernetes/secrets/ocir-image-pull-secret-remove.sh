#!/usr/bin/env bash

# Remove o acesso às imagens privadas do OCIR configurado pelos scripts deste
# diretório. Preserva outros imagePullSecrets associados ao ServiceAccount.

set -euo pipefail

# Nome do Secret criado pelos scripts de configuração do acesso ao OCIR.
secret_name="ocir-secret"

# Define os namespaces nos quais o Secret e sua referência serão removidos.
kubernetes_namespaces=(
  "ocipizza-infra"
  "ocipizza-services"
)

# Exibe as opções aceitas pelo script.
usage() {
  cat <<'EOF'
Uso: ./kubernetes/secrets/ocir-image-pull-secret-remove.sh [opções]

Opções:
  -h, --help   Exibe esta ajuda.

O script remove a referência a ocir-secret do ServiceAccount default e exclui
o Secret dos namespaces ocipizza-infra e ocipizza-services.
EOF
}

# Processa os parâmetros aceitos pelo script.
parse_arguments() {
  while (($# > 0)); do
    case "$1" in
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
}

# Verifica se o kubectl está disponível antes de alterar o cluster atual.
check_dependencies() {
  command -v kubectl >/dev/null 2>&1 || {
    echo "Erro: o comando 'kubectl' não está instalado ou não está no PATH." >&2
    exit 1
  }
}

# Remove somente a referência ao ocir-secret do ServiceAccount default,
# preservando outros imagePullSecrets que possam estar configurados.
remove_service_account_reference() {
  local kubernetes_namespace="$1"
  local image_pull_secret
  local image_pull_secret_index=0

  while IFS= read -r image_pull_secret; do
    if [[ "$image_pull_secret" == "$secret_name" ]]; then
      kubectl patch serviceaccount default \
        --namespace "$kubernetes_namespace" \
        --type json \
        --patch "[{\"op\":\"remove\",\"path\":\"/imagePullSecrets/${image_pull_secret_index}\"}]"

      echo "Referência a ${secret_name} removida do ServiceAccount default."
      return
    fi

    ((image_pull_secret_index += 1))
  done < <(
    kubectl get serviceaccount default \
      --namespace "$kubernetes_namespace" \
      --output jsonpath='{range .imagePullSecrets[*]}{.name}{"\n"}{end}'
  )

  echo "O ServiceAccount default não referencia ${secret_name}; nenhuma alteração necessária."
}

# Remove a configuração do ServiceAccount e o Secret de um namespace.
cleanup_namespace() {
  local kubernetes_namespace="$1"

  if ! kubectl get namespace "$kubernetes_namespace" >/dev/null 2>&1; then
    echo "Namespace ${kubernetes_namespace} não encontrado; ignorando."
    return
  fi

  echo "Removendo acesso ao OCIR do namespace ${kubernetes_namespace}..."

  remove_service_account_reference "$kubernetes_namespace"

  kubectl delete secret "$secret_name" \
    --namespace "$kubernetes_namespace" \
    --ignore-not-found
}

# Coordena a remoção em todos os namespaces utilizados pela aplicação.
main() {
  local kubernetes_namespace

  parse_arguments "$@"
  check_dependencies

  for kubernetes_namespace in "${kubernetes_namespaces[@]}"; do
    cleanup_namespace "$kubernetes_namespace"
  done

  echo "Configuração de acesso às imagens privadas do OCIR removida."
}

main "$@"
