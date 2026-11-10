#!/usr/bin/env bash

# Cria ou atualiza o Secret utilizado para baixar imagens privadas do OCIR e o
# associa ao ServiceAccount padrão dos namespaces da aplicação.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
NAMESPACES_DIR="${SCRIPT_DIR}/../namespaces"

# Usa os valores do ambiente quando os parâmetros correspondentes não forem
# informados na linha de comando.
registry="${REGISTRY:-gru.ocir.io}"
oci_namespace="${OCI_NAMESPACE:-}"
oci_username="${OCI_USERNAME:-}"
oci_auth_token="${OCI_AUTH_TOKEN:-}"
secret_name="ocir-secret"

# Define os namespaces que precisam acessar as imagens privadas do OCIR.
kubernetes_namespaces=(
  "ocipizza-infra"
  "ocipizza-services"
)

# Exibe as opções aceitas pelo script e as variáveis de ambiente equivalentes.
usage() {
  cat <<'EOF'
 ██████╗  ██████╗██╗    ██████╗ ██╗███████╗███████╗ █████╗
██╔═══██╗██╔════╝██║    ██╔══██╗██║╚══███╔╝╚══███╔╝██╔══██╗
██║   ██║██║     ██║    ██████╔╝██║  ███╔╝   ███╔╝ ███████║
██║   ██║██║     ██║    ██╔═══╝ ██║ ███╔╝   ███╔╝  ██╔══██║
╚██████╔╝╚██████╗██║    ██║     ██║███████╗███████╗██║  ██║
 ╚═════╝  ╚═════╝╚═╝    ╚═╝     ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝

   OCI Pizza - by Daniel Armbrust (darmbrust@gmail.com)

Uso: ./kubernetes/secrets/ocir-service-account-setup.sh [opções]

Opções:
  --registry <registry>          Registry do OCIR. Padrão: gru.ocir.io.
  --oci-namespace <namespace>   Namespace da tenancy retornado por oci os ns get.
  --user <usuário>              Nome do usuário do OCI.
  -h, --help                    Exibe esta ajuda.

Os valores também podem ser definidos pelas variáveis de ambiente REGISTRY,
OCI_NAMESPACE, OCI_USERNAME e OCI_AUTH_TOKEN. Quando OCI_AUTH_TOKEN não estiver
definida, o token será solicitado sem ser exibido no terminal.
EOF
}

# Processa os parâmetros e sobrescreve os valores recebidos pelo ambiente.
parse_arguments() {
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

      --user)
        [[ $# -ge 2 ]] || { echo "Erro: --user requer um valor." >&2; exit 1; }
        oci_username="$2"
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
}

# Verifica se os comandos necessários estão instalados antes de alterar o
# cluster configurado no contexto atual do kubectl.
check_dependencies() {
  local command

  for command in kubectl; do
    command -v "$command" >/dev/null 2>&1 || {
      echo "Erro: o comando '$command' não está instalado ou não está no PATH." >&2
      exit 1
    }
  done

  if [[ -z "$oci_namespace" ]]; then
    command -v oci >/dev/null 2>&1 || {
      echo "Erro: informe OCI_NAMESPACE ou instale o OCI CLI." >&2
      exit 1
    }
  fi
}

# Obtém automaticamente o namespace da tenancy quando ele não for informado.
resolve_oci_namespace() {
  if [[ -z "$oci_namespace" ]]; then
    oci_namespace="$(oci os ns get --query data --raw-output)"
  fi

  [[ -n "$oci_namespace" ]] || {
    echo "Erro: não foi possível obter o namespace da tenancy." >&2
    exit 1
  }
}

# Solicita o Auth Token sem exibi-lo quando OCI_AUTH_TOKEN não estiver definida.
resolve_auth_token() {
  if [[ -z "$oci_auth_token" ]]; then
    read -rsp 'Auth Token do OCI: ' oci_auth_token
    echo
  fi

  [[ -n "$oci_auth_token" ]] || {
    echo "Erro: o Auth Token do OCI não pode ser vazio." >&2
    exit 1
  }
}

# Cria ou atualiza o Secret e configura o ServiceAccount padrão do namespace.
configure_namespace() {
  local kubernetes_namespace="$1"

  echo "Configurando acesso ao OCIR no namespace ${kubernetes_namespace}..."

  kubectl create secret docker-registry "$secret_name" \
    --namespace "$kubernetes_namespace" \
    --docker-server "$registry" \
    --docker-username "${oci_namespace}/${oci_username}" \
    --docker-password "$oci_auth_token" \
    --dry-run=client \
    --output yaml \
    | kubectl apply -f -

  kubectl patch serviceaccount default \
    --namespace "$kubernetes_namespace" \
    --type merge \
    --patch "{\"imagePullSecrets\":[{\"name\":\"${secret_name}\"}]}"
}

# Remove o token da variável do processo quando o script terminar.
cleanup() {
  unset oci_auth_token OCI_AUTH_TOKEN
}

# Coordena a validação, a criação dos namespaces e a configuração dos Secrets.
main() {
  local kubernetes_namespace

  parse_arguments "$@"
  check_dependencies
  resolve_oci_namespace

  [[ -n "$oci_username" ]] || {
    echo "Erro: informe OCI_USERNAME ou --user." >&2
    exit 1
  }

  registry="${registry%/}"
  oci_namespace="${oci_namespace%/}"

  resolve_auth_token

  # Os namespaces precisam existir antes que os Secrets sejam criados.
  kubectl apply -f "$NAMESPACES_DIR"

  for kubernetes_namespace in "${kubernetes_namespaces[@]}"; do
    configure_namespace "$kubernetes_namespace"
  done

  echo "Acesso às imagens privadas do OCIR configurado com sucesso."
}

trap cleanup EXIT
main "$@"

exit 0
