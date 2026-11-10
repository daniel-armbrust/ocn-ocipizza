#!/usr/bin/env bash

# Remove o OCI Native Ingress Controller instalado como add-on do cluster OKE.
# O cert-manager também é removido ao final do fluxo.

set -euo pipefail

# Variáveis globais

ADDON_NAME="NativeIngressController"
ADDON_TIMEOUT="900"
ADDON_POLL_INTERVAL="15"
CERT_MANAGER_MANIFEST="https://github.com/jetstack/cert-manager/releases/latest/download/cert-manager.yaml"
REGION="${OCI_REGION:-sa-saopaulo-1}"
OKE_CLUSTER_ID="${OKE_CLUSTER_ID:-}"
OCI_CLI_PROFILE="${OCI_CLI_PROFILE:-DEFAULT}"

# Funções

# Exibe as variáveis necessárias para remover o add-on.
usage() {
  cat <<'EOF'
 ██████╗  ██████╗██╗    ██████╗ ██╗███████╗███████╗ █████╗
██╔═══██╗██╔════╝██║    ██╔══██╗██║╚══███╔╝╚══███╔╝██╔══██╗
██║   ██║██║     ██║    ██████╔╝██║  ███╔╝   ███╔╝ ███████║
██║   ██║██║     ██║    ██╔═══╝ ██║ ███╔╝   ███╔╝  ██╔══██║
╚██████╔╝╚██████╗██║    ██║     ██║███████╗███████╗██║  ██║
 ╚═════╝  ╚═════╝╚═╝    ╚═╝     ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝

   OCI Pizza - by Daniel Armbrust (darmbrust@gmail.com)

Uso: ./undeploy.sh

Variáveis obrigatórias:
  OKE_CLUSTER_ID   OCID do cluster OKE.

Variáveis opcionais:
  OCI_REGION       Região OCI. Padrão: sa-saopaulo-1.
  OCI_CLI_PROFILE  Profile do OCI CLI. Padrão: DEFAULT.

O script remove o add-on NativeIngressController e o cert-manager.
EOF
}

# Verifica se o OCI CLI está instalado e se o OCID do cluster foi informado.
check_dependencies() {
  command -v oci >/dev/null 2>&1 || {
    echo "Erro: o comando 'oci' não está instalado ou não está no PATH." >&2
    exit 1
  }

  command -v kubectl >/dev/null 2>&1 || {
    echo "Erro: o comando 'kubectl' não está instalado ou não está no PATH." >&2
    exit 1
  }

  if [[ -z "$OKE_CLUSTER_ID" ]]; then
    echo "Erro: a variável OKE_CLUSTER_ID deve ser definida." >&2
    usage >&2
    exit 1
  fi
}

# Consulta os add-ons do cluster usando a região e o profile configurados.
list_addons() {
  oci ce cluster list-addons \
    --cluster-id "$OKE_CLUSTER_ID" \
    --region "$REGION" \
    --profile "$OCI_CLI_PROFILE" \
    "$@"
}

# Confirma que o add-on existe antes de solicitar sua remoção.
confirm_addon_installed() {
  local installed_addon

  installed_addon="$(list_addons \
    --query 'data[?name==`NativeIngressController`] | [0].name' \
    --raw-output)"

  if [[ "$installed_addon" != "$ADDON_NAME" ]]; then
    echo "O add-on ${ADDON_NAME} não está instalado; continuando com a remoção do cert-manager."
    return 1
  fi

  return 0
}

# Desabilita o add-on e remove os recursos que ele criou no cluster.
disable_addon() {
  echo "Removendo o add-on ${ADDON_NAME}..."

  oci ce cluster disable-addon \
    --addon-name "$ADDON_NAME" \
    --cluster-id "$OKE_CLUSTER_ID" \
    --region "$REGION" \
    --profile "$OCI_CLI_PROFILE" \
    --is-remove-existing-add-on true
}

# Aguarda o add-on deixar de aparecer na lista do cluster.
wait_for_removal() {
  local installed_addon

  echo "Aguardando a remoção do add-on ${ADDON_NAME}..."

  for ((elapsed = 0; elapsed < ADDON_TIMEOUT; elapsed += ADDON_POLL_INTERVAL)); do
    installed_addon="$(list_addons \
      --query 'data[?name==`NativeIngressController`] | [0].name' \
      --raw-output)"

    if [[ "$installed_addon" != "$ADDON_NAME" ]]; then
      echo "Add-on ${ADDON_NAME} removido com sucesso."
      return 0
    fi

    sleep "$ADDON_POLL_INTERVAL"
  done

  echo "Erro: tempo limite excedido aguardando a remoção do add-on." >&2
  return 1
}

# Remove o cert-manager após o OCI Native Ingress Controller, respeitando a
# ordem de dependências usada durante a instalação.
remove_cert_manager() {
  echo "Removendo o cert-manager..."
  kubectl delete --filename "$CERT_MANAGER_MANIFEST" --ignore-not-found
}

# Fluxo principal

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -gt 0 ]]; then
  echo "Erro: parâmetro desconhecido: $1" >&2
  usage >&2
  exit 1
fi

check_dependencies

if confirm_addon_installed; then
  disable_addon
  wait_for_removal
fi

remove_cert_manager

exit 0