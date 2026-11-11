#!/usr/bin/env bash

# Instala o OCI Native Ingress Controller como add-on do cluster OKE.
# A instalação utiliza o arquivo JSON oficial do add-on renderizado com
# envsubst, sem aplicar manifestos Kubernetes manualmente.

set -euo pipefail

# Variáveis globais

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ADDON_CONFIG_TEMPLATE="${SCRIPT_DIR}/native-ingress-controller-addon.json"
CERT_MANAGER_MANIFEST="https://github.com/jetstack/cert-manager/releases/latest/download/cert-manager.yaml"
CERT_MANAGER_NAMESPACE="cert-manager"
CERT_MANAGER_TIMEOUT="180s"
ADDON_NAME="NativeIngressController"
# Tempo máximo de espera em segundos para o estado ACTIVE.
ADDON_TIMEOUT="900"
ADDON_POLL_INTERVAL="15"
REGION="${OCI_REGION:-sa-saopaulo-1}"
OKE_CLUSTER_ID="${OKE_CLUSTER_ID:-}"
OKE_LOAD_BALANCER_COMPARTMENT_ID="${OKE_LOAD_BALANCER_COMPARTMENT_ID:-}"
OKE_LOAD_BALANCER_SUBNET_ID="${OKE_LOAD_BALANCER_SUBNET_ID:-}"
OCI_NATIVE_INGRESS_AUTH_TYPE="${OCI_NATIVE_INGRESS_AUTH_TYPE:-instance}"
OCI_NATIVE_INGRESS_LOG_VERBOSITY="${OCI_NATIVE_INGRESS_LOG_VERBOSITY:-2}"
OCI_CLI_PROFILE="${OCI_CLI_PROFILE:-DEFAULT}"
RENDERED_ADDON_CONFIG=""

# Funções

# Exibe as variáveis necessárias e o comando de instalação do add-on.
usage() {
  cat <<'EOF'
 ██████╗  ██████╗██╗    ██████╗ ██╗███████╗███████╗ █████╗
██╔═══██╗██╔════╝██║    ██╔══██╗██║╚══███╔╝╚══███╔╝██╔══██╗
██║   ██║██║     ██║    ██████╔╝██║  ███╔╝   ███╔╝ ███████║
██║   ██║██║     ██║    ██╔═══╝ ██║ ███╔╝   ███╔╝  ██╔══██║
╚██████╔╝╚██████╗██║    ██║     ██║███████╗███████╗██║  ██║
 ╚═════╝  ╚═════╝╚═╝    ╚═╝     ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝

   OCI Pizza - by Daniel Armbrust (darmbrust@gmail.com)

Uso: ./deploy.sh

Variáveis obrigatórias:
  OKE_CLUSTER_ID                     OCID do cluster OKE.
  OKE_LOAD_BALANCER_COMPARTMENT_ID   OCID do compartment que receberá o Load Balancer.
  OKE_LOAD_BALANCER_SUBNET_ID        OCID da sub-rede dos Load Balancers.

Variáveis opcionais:
  OCI_REGION                         Região OCI. Padrão: sa-saopaulo-1.
  OCI_NATIVE_INGRESS_AUTH_TYPE       Autenticação do add-on. Padrão: instance.
  OCI_NATIVE_INGRESS_LOG_VERBOSITY   Verbosidade dos logs. Padrão: 2.
  OCI_CLI_PROFILE                    Profile do OCI CLI. Padrão: DEFAULT.

O script instala o cert-manager antes do add-on usando o manifesto oficial.
EOF
}

# Verifica os comandos e o arquivo necessários antes de iniciar a instalação.
check_dependencies() {
  command -v oci >/dev/null 2>&1 || {
    echo "Erro: o comando 'oci' não está instalado ou não está no PATH." >&2
    exit 1
  }

  command -v envsubst >/dev/null 2>&1 || {
    echo "Erro: o comando 'envsubst' não está instalado ou não está no PATH." >&2
    exit 1
  }

  command -v kubectl >/dev/null 2>&1 || {
    echo "Erro: o comando 'kubectl' não está instalado ou não está no PATH." >&2
    exit 1
  }

  [[ -f "$ADDON_CONFIG_TEMPLATE" ]] || {
    echo "Erro: arquivo não encontrado: $ADDON_CONFIG_TEMPLATE" >&2
    exit 1
  }
}

# Instala o cert-manager antes do OCI Native Ingress Controller, pois o add-on
# utiliza seus certificados para o webhook de readiness gates.
install_cert_manager() {
  echo "Instalando o cert-manager..."
  kubectl apply --filename "$CERT_MANAGER_MANIFEST"

  for deployment_name in cert-manager cert-manager-cainjector cert-manager-webhook; do
    echo "Aguardando o Deployment ${deployment_name}..."
    
    kubectl rollout status "deployment/${deployment_name}" \
      --namespace "$CERT_MANAGER_NAMESPACE" \
      --timeout "$CERT_MANAGER_TIMEOUT"
  done
}

# Consulta os add-ons instalados no cluster usando o mesmo profile e região
# que serão utilizados na instalação do OCI Native Ingress Controller.
list_addons() {
  oci ce cluster list-addons \
    --cluster-id "$OKE_CLUSTER_ID" \
    --region "$REGION" \
    --profile "$OCI_CLI_PROFILE" \
    "$@"
}

# Impede a instalação duplicada do add-on no mesmo cluster.
confirm_addon_not_installed() {
  local installed_addon

  echo "Verificando se o add-on ${ADDON_NAME} já está instalado..."
  
  installed_addon="$(list_addons \
    --query 'data[?name==`NativeIngressController`] | [0].name' \
    --raw-output)"

  if [[ "$installed_addon" == "$ADDON_NAME" ]]; then
    echo "Erro: o add-on ${ADDON_NAME} já está instalado no cluster." >&2
    exit 1
  fi

  echo "O add-on ${ADDON_NAME} ainda não está instalado."
}

# Valida os OCIDs e demais valores necessários para o arquivo do add-on.
validate_configuration() {
  local variable_name variable_value

  for variable_name in OKE_CLUSTER_ID OKE_LOAD_BALANCER_COMPARTMENT_ID OKE_LOAD_BALANCER_SUBNET_ID; do
    variable_value="${!variable_name}"
    
    if [[ -z "$variable_value" ]]; then
      echo "Erro: a variável ${variable_name} deve ser definida." >&2
      usage >&2
      exit 1
    fi
  
  done

  if [[ "$OCI_NATIVE_INGRESS_AUTH_TYPE" != "instance" && \
    "$OCI_NATIVE_INGRESS_AUTH_TYPE" != "workloadIdentity" && \
    "$OCI_NATIVE_INGRESS_AUTH_TYPE" != "user" ]]; then
  
    echo "Erro: OCI_NATIVE_INGRESS_AUTH_TYPE deve ser instance, workloadIdentity ou user." >&2
    exit 1
  fi
}

# Remove o arquivo temporário gerado pelo envsubst ao finalizar o script.
cleanup() {
  if [[ -n "$RENDERED_ADDON_CONFIG" && -f "$RENDERED_ADDON_CONFIG" ]]; then
    rm -f -- "$RENDERED_ADDON_CONFIG"
  fi
}

# Renderiza o JSON substituindo somente as variáveis usadas pelo add-on.
render_addon_configuration() {
  RENDERED_ADDON_CONFIG="$(mktemp "${TMPDIR:-/tmp}/native-ingress-controller-addon.XXXXXX.json")"
  chmod 600 "$RENDERED_ADDON_CONFIG"

  # envsubst lê somente variáveis exportadas pelo ambiente do processo.
  # Re-renderiza com os valores efetivos definidos pelo script, inclusive os
  # padrões de autenticação e verbosidade.
  OKE_LOAD_BALANCER_COMPARTMENT_ID="$OKE_LOAD_BALANCER_COMPARTMENT_ID" \
  OKE_LOAD_BALANCER_SUBNET_ID="$OKE_LOAD_BALANCER_SUBNET_ID" \
  OCI_NATIVE_INGRESS_AUTH_TYPE="$OCI_NATIVE_INGRESS_AUTH_TYPE" \
  OCI_NATIVE_INGRESS_LOG_VERBOSITY="$OCI_NATIVE_INGRESS_LOG_VERBOSITY" \
    envsubst \
      '${OKE_LOAD_BALANCER_COMPARTMENT_ID} ${OKE_LOAD_BALANCER_SUBNET_ID} ${OCI_NATIVE_INGRESS_AUTH_TYPE} ${OCI_NATIVE_INGRESS_LOG_VERBOSITY}' \
      < "$ADDON_CONFIG_TEMPLATE" \
      > "$RENDERED_ADDON_CONFIG"

  if grep -qE '"value"[[:space:]]*:[[:space:]]*""' "$RENDERED_ADDON_CONFIG"; then
    echo "Erro: o JSON renderizado contém uma configuração vazia." >&2
    exit 1
  fi
}

# Instala o OCI Native Ingress Controller usando a API de add-ons do OKE.
install_addon() {
  local -a oci_arguments=(
    ce cluster install-addon
    --addon-name "$ADDON_NAME"
    --cluster-id "$OKE_CLUSTER_ID"
    --region "$REGION"
    --profile "$OCI_CLI_PROFILE"
    --from-json "file://${RENDERED_ADDON_CONFIG}"
  )

  echo "Instalando o OCI Native Ingress Controller como add-on..."
  oci "${oci_arguments[@]}"
}

# Aguarda o add-on concluir a instalação e interrompe em caso de falha.
wait_for_addon() {
  local addon_state

  echo "Aguardando a conclusão do deployment do add-on ${ADDON_NAME}..."

  for ((elapsed = 0; elapsed < ADDON_TIMEOUT; elapsed += ADDON_POLL_INTERVAL)); do
    addon_state="$(list_addons \
      --query 'data[?name==`NativeIngressController`] | [0]."lifecycle-state"' \
      --raw-output)"

    case "$addon_state" in
      ACTIVE)
        echo "Add-on ${ADDON_NAME} instalado com sucesso (ACTIVE)."
        return 0
        ;;
      
      FAILED | DELETED | DELETING)
        echo "Erro: o add-on ${ADDON_NAME} terminou no estado ${addon_state}." >&2
        return 1
        ;;
      
      "" | None | null)
        echo "Estado do add-on ainda não disponível; aguardando..."
        ;;
      
      *)
        echo "Estado atual do add-on ${ADDON_NAME}: ${addon_state}"
        ;;
    esac

    sleep "$ADDON_POLL_INTERVAL"
  done

  echo "Erro: tempo limite excedido aguardando o add-on ${ADDON_NAME}." >&2
  return 1
}

# Fluxo principal

trap cleanup EXIT

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
validate_configuration
confirm_addon_not_installed
install_cert_manager
render_addon_configuration
install_addon
wait_for_addon

exit 0
