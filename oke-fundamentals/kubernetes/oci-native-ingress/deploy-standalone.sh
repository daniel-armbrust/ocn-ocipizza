#!/usr/bin/env bash

# Instala o OCI Native Ingress Controller como um programa standalone.
# O fluxo segue a documentação oficial do OKE e utiliza o Helm diretamente,
# sem depender do gerenciamento de add-ons do cluster.

set -euo pipefail

# Variáveis globais

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
OCI_NATIVE_INGRESS_REPOSITORY="https://github.com/oracle/oci-native-ingress-controller.git"
CERT_MANAGER_MANIFEST="https://github.com/jetstack/cert-manager/releases/latest/download/cert-manager.yaml"
CERT_MANAGER_NAMESPACE="cert-manager"
CERT_MANAGER_TIMEOUT="180s"
CERT_MANAGER_CA_TIMEOUT=180
CERT_MANAGER_CA_POLL_INTERVAL=5
NATIVE_INGRESS_NAMESPACE="native-ingress-controller-system"
RELEASE_NAME="oci-native-ingress-controller"
CONTROLLER_READY_TIMEOUT=180
CONTROLLER_READY_POLL_INTERVAL=5
REPLICA_COUNT="2"
INGRESS_CLASS_PARAMETERS_MANIFEST="${SCRIPT_DIR}/IngressClassParameters.yaml"
INGRESS_CLASS_MANIFEST="${SCRIPT_DIR}/IngressClass.yaml"
INGRESS_MANIFEST="${SCRIPT_DIR}/Ingress.yaml"
OKE_CLUSTER_ID="${OKE_CLUSTER_ID:-}"
OKE_LOAD_BALANCER_COMPARTMENT_ID="${OKE_LOAD_BALANCER_COMPARTMENT_ID:-}"
OKE_LOAD_BALANCER_SUBNET_ID="${OKE_LOAD_BALANCER_SUBNET_ID:-}"
OCI_NATIVE_INGRESS_AUTH_TYPE="${OCI_NATIVE_INGRESS_AUTH_TYPE:-instance}"
TEMP_DIR=""
REPOSITORY_DIR=""
VALUES_FILE=""

# Funções

# Exibe a forma de uso, as variáveis obrigatórias e as variáveis opcionais.
usage() {
  cat <<'EOF'
 ██████╗  ██████╗██╗    ██████╗ ██╗███████╗███████╗ █████╗
██╔═══██╗██╔════╝██║    ██╔══██╗██║╚══███╔╝╚══███╔╝██╔══██╗
██║   ██║██║     ██║    ██████╔╝██║  ███╔╝   ███╔╝ ███████║
██║   ██║██║     ██║    ██╔═══╝ ██║ ███╔╝   ███╔╝  ██╔══██║
╚██████╔╝╚██████╗██║    ██║     ██║███████╗███████╗██║  ██║
 ╚═════╝  ╚═════╝╚═╝    ╚═╝     ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝

   OCI Pizza - by Daniel Armbrust (darmbrust@gmail.com)

Uso: ./deploy-standalone.sh

Variáveis obrigatórias:
  OKE_CLUSTER_ID                     OCID do cluster OKE.
  OKE_LOAD_BALANCER_COMPARTMENT_ID   OCID do compartment dos Load Balancers.
  OKE_LOAD_BALANCER_SUBNET_ID        OCID da sub-rede dos Load Balancers.

Variáveis opcionais:
  OCI_NATIVE_INGRESS_AUTH_TYPE       Tipo de autenticação. Padrão: instance.

O script instala o cert-manager, clona o repositório oficial e instala
o OCI Native Ingress Controller via Helm no modo standalone.
EOF
}

# Remove o clone temporário ao encerrar o script, inclusive em caso de erro.
cleanup() {
  if [[ -n "$TEMP_DIR" && -d "$TEMP_DIR" ]]; then
    rm -rf -- "$TEMP_DIR"
  fi
}

# Verifica se as ferramentas necessárias estão disponíveis no PATH.
check_dependencies() {
  local command_name

  # O Git é necessário para clonar o repositório oficial do controlador.
  for command_name in helm kubectl git envsubst; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
      echo "Erro: o comando '${command_name}' não está instalado ou não está no PATH." >&2
      exit 1
    fi
  done
}

# Verifica as variáveis que identificam o cluster e a sub-rede do Load Balancer.
validate_configuration() {
  local variable_name
  local missing=0

  for variable_name in \
    OKE_CLUSTER_ID \
    OKE_LOAD_BALANCER_COMPARTMENT_ID \
    OKE_LOAD_BALANCER_SUBNET_ID; do
    
    if [[ -z "${!variable_name}" ]]; then
      echo "Erro: a variável ${variable_name} deve ser definida." >&2
      missing=1
    fi
  done

  if [[ "$missing" -ne 0 ]]; then
    usage >&2
    exit 1
  fi

  case "$OCI_NATIVE_INGRESS_AUTH_TYPE" in
    instance|user)
      ;;

    *)
      echo "Erro: OCI_NATIVE_INGRESS_AUTH_TYPE deve ser 'instance' ou 'user'." >&2
      exit 1
      ;;
  esac
}

# Instala o cert-manager usando o manifesto oficial e aguarda os deployments.
install_cert_manager() {
  echo "Instalando o Cert-Manager..."
  kubectl apply --filename "$CERT_MANAGER_MANIFEST"

  for deployment_name in cert-manager cert-manager-cainjector cert-manager-webhook; do
    kubectl rollout status \
      "deployment/${deployment_name}" \
      --namespace "$CERT_MANAGER_NAMESPACE" \
      --timeout "$CERT_MANAGER_TIMEOUT"
  done

  # O cainjector pode precisar de alguns segundos para preencher a CA no
  # webhook. Sem esse valor, o API Server pode rejeitar o Helm com erro x509.
  wait_for_cert_manager_ca
}

# Aguarda o cainjector publicar a CA no webhook de validação do Cert-Manager.
wait_for_cert_manager_ca() {
  local elapsed=0
  local ca_bundle

  echo "Aguardando a CA do webhook do Cert-Manager..."

  while (( elapsed < CERT_MANAGER_CA_TIMEOUT )); do
    ca_bundle="$(kubectl get validatingwebhookconfiguration cert-manager-webhook \
      --output=jsonpath='{.webhooks[0].clientConfig.caBundle}' 2>/dev/null || true)"

    if [[ -n "$ca_bundle" ]]; then
      return 0
    fi

    sleep "$CERT_MANAGER_CA_POLL_INTERVAL"
    (( elapsed += CERT_MANAGER_CA_POLL_INTERVAL ))
  done

  echo "Erro: tempo limite aguardando a CA do webhook do Cert-Manager." >&2
  exit 1
}

# Clona o repositório oficial em um diretório temporário.
clone_repository() {
  TEMP_DIR="$(mktemp -d)"
  REPOSITORY_DIR="${TEMP_DIR}/oci-native-ingress-controller"

  echo "Clonando o repositório do OCI Native Ingress Controller..."
  git clone --depth 1 "$OCI_NATIVE_INGRESS_REPOSITORY" "$REPOSITORY_DIR"

  VALUES_FILE="${REPOSITORY_DIR}/helm/oci-native-ingress-controller/values.yaml"
  
  if [[ ! -f "$VALUES_FILE" ]]; then
    echo "Erro: values.yaml não encontrado em ${VALUES_FILE}." >&2
    exit 1
  fi
}

# Atualiza uma chave YAML textual, preservando o nível superior do values.yaml.
set_yaml_string() {
  local key="$1"
  local value="$2"

  sed -i -E "s|^(${key}:[[:space:]]*).*$|\1\"${value}\"|" "$VALUES_FILE"
}

# Atualiza uma chave YAML numérica sem convertê-la para string.
set_yaml_number() {
  local key="$1"
  local value="$2"

  sed -i -E "s|^(${key}:[[:space:]]*).*$|\1${value}|" "$VALUES_FILE"
}

# Preenche o values.yaml com os parâmetros do cluster e do Load Balancer.
prepare_values() {
  echo "Configurando o values.yaml..."
  
  set_yaml_string "compartment_id" "$OKE_LOAD_BALANCER_COMPARTMENT_ID"
  set_yaml_string "subnet_id" "$OKE_LOAD_BALANCER_SUBNET_ID"
  set_yaml_string "cluster_id" "$OKE_CLUSTER_ID"
  set_yaml_string "authType" "$OCI_NATIVE_INGRESS_AUTH_TYPE"
  set_yaml_number "replicaCount" "$REPLICA_COUNT"
}

# Instala o chart no namespace padrão do controlador usando Helm.
install_controller() {
  echo "Instalando o OCI Native Ingress Controller via Helm..."

  # O namespace pode ter sido criado por uma tentativa anterior. Aplicar o
  # manifesto de forma idempotente evita o erro AlreadyExists.
  kubectl create namespace "$NATIVE_INGRESS_NAMESPACE" \
    --dry-run=client \
    --output yaml | kubectl apply --filename -

  # Uma instalação que falhou pode deixar um release com status failed. Nesse
  # caso, removemos somente o registro incompleto para permitir nova tentativa.
  if helm status "$RELEASE_NAME" --namespace "$NATIVE_INGRESS_NAMESPACE" \
    --output json 2>/dev/null | grep -q '"status":"failed"'; then
    echo "Removendo o release Helm que falhou anteriormente..."
    helm uninstall "$RELEASE_NAME" --namespace "$NATIVE_INGRESS_NAMESPACE"
  fi

  helm install "$RELEASE_NAME" \
    "$REPOSITORY_DIR/helm/oci-native-ingress-controller" \
    --namespace "$NATIVE_INGRESS_NAMESPACE" \
    --values "$VALUES_FILE"
}

# Aguarda pelo menos uma réplica líder pronta e exibe o estado das réplicas.
verify_installation() {
  local elapsed=0
  local ready_status

  echo "Aguardando o OCI Native Ingress Controller..."

  # A réplica standby participa da eleição, mas não inicia os controllers e
  # pode manter /healthz/ready em 503. Basta uma réplica líder estar pronta.
  while (( elapsed < CONTROLLER_READY_TIMEOUT )); do
    ready_status="$(kubectl get pods \
      --namespace "$NATIVE_INGRESS_NAMESPACE" \
      --selector='app.kubernetes.io/name=oci-native-ingress-controller' \
      --output=jsonpath='{range .items[*]}{.status.conditions[?(@.type=="Ready")].status}{"\n"}{end}')"

    if grep -qx "True" <<<"$ready_status"; then
      kubectl get pods \
        --namespace "$NATIVE_INGRESS_NAMESPACE" \
        --selector='app.kubernetes.io/name=oci-native-ingress-controller' \
        --output wide
      return 0
    fi

    sleep "$CONTROLLER_READY_POLL_INTERVAL"
    (( elapsed += CONTROLLER_READY_POLL_INTERVAL ))
  done

  echo "Erro: nenhuma réplica do OCI Native Ingress Controller ficou Ready dentro do tempo esperado." >&2
  kubectl get pods \
    --namespace "$NATIVE_INGRESS_NAMESPACE" \
    --selector='app.kubernetes.io/name=oci-native-ingress-controller' \
    --output wide >&2
  exit 1
}

# Aplica os recursos de roteamento somente depois que o controlador estiver
# disponível, respeitando a ordem IngressClassParameters, IngressClass e Ingress.
apply_ingress_resources() {
  local manifest_path

  for manifest_path in \
    "$INGRESS_CLASS_PARAMETERS_MANIFEST" \
    "$INGRESS_CLASS_MANIFEST" \
    "$INGRESS_MANIFEST"; do
    if [[ ! -f "$manifest_path" ]]; then
      echo "Erro: manifesto não encontrado: ${manifest_path}" >&2
      exit 1
    fi
  done

  echo "Aplicando IngressClassParameters.yaml..."
  OKE_LOAD_BALANCER_COMPARTMENT_ID="$OKE_LOAD_BALANCER_COMPARTMENT_ID" \
  OKE_LOAD_BALANCER_SUBNET_ID="$OKE_LOAD_BALANCER_SUBNET_ID" \
    envsubst '${OKE_LOAD_BALANCER_COMPARTMENT_ID} ${OKE_LOAD_BALANCER_SUBNET_ID}' \
      < "$INGRESS_CLASS_PARAMETERS_MANIFEST" | kubectl apply --filename -

  echo "Aplicando IngressClass.yaml..."
  kubectl apply --filename "$INGRESS_CLASS_MANIFEST"

  echo "Aplicando Ingress.yaml..."
  kubectl apply --filename "$INGRESS_MANIFEST"
}

# Execução principal

trap cleanup EXIT

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

if [[ "$#" -ne 0 ]]; then
  echo "Erro: argumento não reconhecido: $1" >&2
  usage >&2
  exit 1
fi

check_dependencies
validate_configuration
install_cert_manager
clone_repository
prepare_values
install_controller
verify_installation
apply_ingress_resources

echo "OCI Native Ingress Controller instalado com sucesso no modo standalone."

exit 0
