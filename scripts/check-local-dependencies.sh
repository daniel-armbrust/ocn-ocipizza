#!/usr/bin/env bash

# Verifica, sem instalar ou modificar o ambiente, as dependências necessárias
# para executar a OCI Pizza localmente com Make, Docker Compose e os scripts de
# bootstrap dos serviços.

set -uo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
MISSING_REQUIRED=0
MISSING_OKE=0
MISSING_OPTIONAL=0

# Exibe a identidade visual da OCI Pizza antes das verificações.
display_ocipizza_banner() {
  printf '%s\n' ''
  printf '%s\n' ' ██████╗  ██████╗██╗    ██████╗ ██╗███████╗███████╗ █████╗ '
  printf '%s\n' '██╔═══██╗██╔════╝██║    ██╔══██╗██║╚══███╔╝╚══███╔╝██╔══██╗'
  printf '%s\n' '██║   ██║██║     ██║    ██████╔╝██║  ███╔╝   ███╔╝ ███████║'
  printf '%s\n' '██║   ██║██║     ██║    ██╔═══╝ ██║ ███╔╝   ███╔╝  ██╔══██║'
  printf '%s\n' '╚██████╔╝╚██████╗██║    ██║     ██║███████╗███████╗██║  ██║'
  printf '%s\n' ' ╚═════╝  ╚═════╝╚═╝    ╚═╝     ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝'
  printf '%s\n' ''
  printf '%s\n' '   OCI Pizza - Verificação de dependências locais'
  printf '%s\n' ''
}

# Exibe o resultado de uma verificação com uma identificação uniforme.
print_result() {
  local status="$1"
  local name="$2"
  local details="$3"

  printf '  [%-9s] %-20s %s\n' "$status" "$name" "$details"
}

# Verifica um binário obrigatório para o ambiente local padrão.
check_required_command() {
  local command_name="$1"
  local purpose="$2"
  local executable

  executable="$(command -v "$command_name" 2>/dev/null || true)"

  if [[ -n "$executable" ]]; then
    print_result 'OK' "$command_name" "$executable"
  else
    print_result 'AUSENTE' "$command_name" "$purpose"
    MISSING_REQUIRED=$((MISSING_REQUIRED + 1))
  fi
}

# Verifica um binário usado apenas por integrações ou automações opcionais.
check_optional_command() {
  local command_name="$1"
  local purpose="$2"
  local executable

  executable="$(command -v "$command_name" 2>/dev/null || true)"

  if [[ -n "$executable" ]]; then
    print_result 'OK' "$command_name" "$executable"
  else
    print_result 'OPCIONAL' "$command_name" "$purpose"
    MISSING_OPTIONAL=$((MISSING_OPTIONAL + 1))
  fi
}

# Verifica um binário necessário para executar integralmente o laboratório
# oke-fundamentals, sem misturá-lo às dependências do Docker Compose local.
check_oke_command() {
  local command_name="$1"
  local purpose="$2"
  local executable

  executable="$(command -v "$command_name" 2>/dev/null || true)"

  if [[ -n "$executable" ]]; then
    print_result 'OK' "$command_name" "$executable"
  else
    print_result 'AUSENTE' "$command_name" "$purpose"
    MISSING_OKE=$((MISSING_OKE + 1))
  fi
}

# Confirma que o Docker possui o plugin Compose v2 usado pelo Makefile.
check_docker_compose() {
  if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    print_result 'OK' 'docker compose' "$(docker compose version --short 2>/dev/null || echo 'Compose v2 disponível')"
  else
    print_result 'AUSENTE' 'docker compose' 'plugin Compose v2 exigido pelo Makefile'
    MISSING_REQUIRED=$((MISSING_REQUIRED + 1))
  fi
}

# Verifica se a instalação do Python consegue criar ambientes virtuais.
check_python_venv() {
  if command -v python3.11 >/dev/null 2>&1 && python3.11 -m venv --help >/dev/null 2>&1; then
    print_result 'OK' 'python3.11-venv' 'módulo venv disponível'
  else
    print_result 'AUSENTE' 'python3.11-venv' 'necessário pelos scripts bootstrap.sh'
    MISSING_REQUIRED=$((MISSING_REQUIRED + 1))
  fi
}

# Informa se o daemon Docker está acessível sem transformar isso em uma
# dependência de instalação ausente.
check_docker_daemon() {
  if ! command -v docker >/dev/null 2>&1; then
    return
  fi

  if docker info >/dev/null 2>&1; then
    print_result 'OK' 'Docker daemon' 'acessível pelo usuário atual'
  else
    print_result 'ATENÇÃO' 'Docker daemon' 'não está iniciado ou o usuário não possui acesso'
    MISSING_REQUIRED=$((MISSING_REQUIRED + 1))
  fi
}

# Verifica arquivos locais que são gerados pelo bootstrap e montados pelo
# Docker Compose, sem revelar nem inspecionar seu conteúdo.
check_generated_files() {
  local private_key="${PROJECT_ROOT}/services/user-service/secrets/jwt_private_key.pem"
  local public_key="${PROJECT_ROOT}/services/user-service/secrets/jwt_public_key.pem"

  if [[ -s "$private_key" && -s "$public_key" ]]; then
    print_result 'OK' 'chaves JWT' 'par de chaves local presente'
  else
    print_result 'PENDENTE' 'chaves JWT' 'serão geradas por services/user-service/bootstrap.sh'
  fi
}

# Executa todas as verificações e retorna erro somente quando uma dependência
# obrigatória não está disponível.
main() {
  display_ocipizza_banner

  printf '\nDependências obrigatórias para execução local:\n\n'

  check_required_command bash 'shell exigido pelos scripts do projeto'
  check_required_command make 'orquestra os alvos de desenvolvimento'
  check_required_command docker 'executa containers e constrói imagens'
  check_docker_compose
  check_docker_daemon
  check_required_command python3.11 'executa os bootstraps dos serviços'
  check_python_venv
  check_required_command openssl 'gera as chaves JWT locais'
  check_required_command mysql 'cria o banco e o usuário do user-service'
  check_required_command mysqladmin 'aguarda a disponibilidade do MySQL'
  check_required_command curl 'aguarda endpoints HTTP da infraestrutura'
  check_required_command timeout 'aguarda portas TCP da infraestrutura'
  check_required_command redis-cli 'aguarda a disponibilidade do Redis'

  printf '\nDependências do laboratório oke-fundamentals:\n\n'

  check_oke_command terraform 'provisiona a infraestrutura do laboratório'
  check_oke_command oci 'gera kubeconfig e administra recursos OCI/OKE'
  check_oke_command kubectl 'aplica e inspeciona os recursos Kubernetes'
  check_oke_command helm 'instala os controllers Kubernetes demonstrados'
  check_oke_command envsubst 'renderiza variáveis nos manifests Kubernetes'
  check_oke_command ssh-keygen 'gera as chaves dos worker nodes'
  check_oke_command git 'obtém fontes usadas por controllers do laboratório'
  check_oke_command awk 'processa saídas nos scripts dos controllers'

  printf '\nDependências para integrações e automações opcionais:\n\n'

  check_optional_command jq 'necessário para scripts Terraform/OCI e publicação no OCIR'

  printf '\nArquivos gerados localmente:\n\n'
  check_generated_files

  printf '\nResumo:\n'

  if ((MISSING_REQUIRED > 0)); then
    printf '  %d dependência(s) obrigatória(s) ausente(s) ou indisponível(is).\n' "$MISSING_REQUIRED"
  else
    printf '  Todas as dependências obrigatórias estão disponíveis.\n'
  fi

  if ((MISSING_OPTIONAL > 0)); then
    printf '  %d dependência(s) opcional(is) não encontrada(s).\n' "$MISSING_OPTIONAL"
  else
    printf '  Todas as dependências opcionais verificadas estão disponíveis.\n'
  fi

  if ((MISSING_OKE > 0)); then
    printf '  %d dependência(s) do oke-fundamentals ausente(s).\n' "$MISSING_OKE"
  else
    printf '  Todas as dependências do oke-fundamentals estão disponíveis.\n'
  fi

  printf '\n'
  ((MISSING_REQUIRED == 0 && MISSING_OKE == 0))
}

main "$@"
