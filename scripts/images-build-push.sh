#!/usr/bin/env bash

#
# images-build-push.sh - OCI Pizza
#
# Constrói as imagens dos serviços da aplicação, aplica as tags esperadas pelo
# OCI Container Registry e publica as imagens no OCIR de São Paulo.
#
# Uso:
#   ./scripts/images-build-push.sh --user <usuario>
#   ./scripts/images-build-push.sh --user <usuario> --no-cache
#   ./scripts/images-build-push.sh --tag <versão> --remove
#

set -euo pipefail

# Resolve os caminhos a partir da localização do script para permitir sua
# execução a partir de qualquer diretório do sistema.
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
readonly SERVICES_DIR="${PROJECT_ROOT}/services"
readonly DOCKER_CONFIG_DIR="${DOCKER_CONFIG:-${HOME}/.docker}"
readonly DOCKER_CONFIG_FILE="${DOCKER_CONFIG_DIR}/config.json"
readonly OCI_CONFIG_FILE="${OCI_CLI_CONFIG_FILE:-${HOME}/.oci/config}"
readonly OCI_CONFIG_PROFILE="${OCI_CLI_PROFILE:-DEFAULT}"

# O laboratório utiliza o OCIR da região de São Paulo e workers x86_64.
readonly OCIR_REGISTRY="gru.ocir.io"
readonly DEFAULT_REPOSITORY_PREFIX="ocipizza"
readonly DEFAULT_IMAGE_TAG="1.0.0"
readonly TARGET_PLATFORM="linux/amd64"

# Valores informados pelo operador. O usuário é obrigatório somente no fluxo
# de build e push; os demais possuem defaults adequados ao laboratório.
oci_user=""
repository_prefix="${DEFAULT_REPOSITORY_PREFIX}"
image_tag="${DEFAULT_IMAGE_TAG}"
no_cache=false
remove_local_images=false

# Mantém a documentação de uso junto ao parser das opções suportadas.
usage() {
    cat <<'EOF'
Uso:
  images-build-push.sh --user <usuario> [opções]

Opções:
  --user <usuario>              Usuário OCI usado no login do OCIR. Obrigatório
                                para build e push; dispensado com --remove.
                                Para outro Identity Domain, informe
                                <identity-domain>/<usuario>.
  --tag <versão>                Tag das imagens. Padrão: 1.0.0.
  --repository-prefix <prefixo> Prefixo dos repositórios. Padrão: ocipizza.
  --no-cache                    Executa o docker build sem utilizar cache.
  --remove                      Exclui imagens, repositórios OCIR e imagens
                                locais, sem executar build, tag ou push.
  -h, --help                    Exibe esta ajuda.

Exemplos:
  images-build-push.sh --user usuario@example.com
  images-build-push.sh --user Default/usuario@example.com --tag 1.1.0 --no-cache
  images-build-push.sh --tag 1.0.0 --remove

O namespace da tenancy é consultado automaticamente com `oci os ns get`.
Durante o `docker login`, informe um Auth Token da OCI como senha.
EOF
}

# Centraliza a saída de erros para garantir mensagens consistentes em stderr.
fail() {
    echo "Erro: $*" >&2
    exit 1
}

# Evita que uma opção seguinte seja interpretada como valor da opção atual.
require_option_value() {
    local option="$1"
    local value="${2:-}"

    if [[ -z "${value}" || "${value}" == --* ]]; then
        fail "a opção ${option} exige um valor."
    fi
}

# O OCID do Root Compartment é o próprio OCID da tenancy. A variável de
# ambiente tem precedência; caso não exista, o valor é lido do profile ativo
# sem imprimir outros campos potencialmente sensíveis do arquivo OCI.
get_root_compartment_id() {
    if [[ -n "${OCI_CLI_TENANCY:-}" ]]; then
        printf '%s\n' "${OCI_CLI_TENANCY}"
        return 0
    fi

    [[ -f "${OCI_CONFIG_FILE}" ]] || return 1

    awk -v wanted_profile="[${OCI_CONFIG_PROFILE}]" '
        /^\[/ {
            active_profile = ($0 == wanted_profile)
            next
        }
        active_profile && /^[[:space:]]*tenancy[[:space:]]*=/ {
            sub(/^[^=]*=[[:space:]]*/, "")
            sub(/[[:space:]\r]+$/, "")
            print
            exit
        }
    ' "${OCI_CONFIG_FILE}"
}

# Aceita opções nos formatos `--opção valor` e `--opção=valor`, facilitando o
# uso manual e a chamada por outras automações.
while (($# > 0)); do
    case "$1" in
        --user)
            require_option_value "$1" "${2:-}"
            oci_user="$2"
            shift 2
            ;;

        --user=*)
            oci_user="${1#*=}"
            [[ -n "${oci_user}" ]] || fail "a opção --user exige um valor."
            shift
            ;;

        --tag)
            require_option_value "$1" "${2:-}"
            image_tag="$2"
            shift 2
            ;;

        --tag=*)
            image_tag="${1#*=}"
            [[ -n "${image_tag}" ]] || fail "a opção --tag exige um valor."
            shift
            ;;

        --repository-prefix)
            require_option_value "$1" "${2:-}"
            repository_prefix="$2"
            shift 2
            ;;

        --repository-prefix=*)
            repository_prefix="${1#*=}"
            [[ -n "${repository_prefix}" ]] || fail "a opção --repository-prefix exige um valor."
            shift
            ;;

        --no-cache)
            no_cache=true
            shift
            ;;

        --remove)
            remove_local_images=true
            shift
            ;;

        -h | --help)
            usage
            exit 0
            ;;

        *)
            fail "opção desconhecida: $1. Use --help para consultar o uso."
            ;;
    esac
done

# Valida os argumentos antes de executar comandos que autenticam ou modificam
# o registry remoto.
if [[ "${remove_local_images}" == false ]]; then
    [[ -n "${oci_user}" ]] || fail "informe o usuário OCI com --user."
fi

[[ "${image_tag}" != *[[:space:]]* ]] || fail "a tag da imagem não pode conter espaços."

[[ "${repository_prefix}" != /* && "${repository_prefix}" != */ ]] || \
    fail "o prefixo do repositório não pode começar nem terminar com '/'."

# Falha antecipadamente quando uma dependência local não está disponível. O
# jq é usado somente para inspecionar a configuração de autenticação do Docker.
for command in oci docker jq awk; do
    command -v "${command}" >/dev/null 2>&1 || fail "comando não encontrado: ${command}."
done

# O namespace do Object Storage identifica a tenancy nos caminhos do OCIR e
# no nome usado durante o login. Ele não deve ser confundido com o nome da
# tenancy exibido na Console.
tenancy_namespace="$(oci os ns get --query data --raw-output)"

[[ -n "${tenancy_namespace}" && "${tenancy_namespace}" != "null" ]] || \
    fail "não foi possível obter o namespace da tenancy com o OCI CLI."

# Descobre somente Dockerfiles no primeiro nível de cada serviço. O uso de
# delimitador nulo preserva corretamente caminhos que eventualmente contenham
# espaços, e a ordenação torna a execução previsível.
mapfile -d '' dockerfiles < <(
    find "${SERVICES_DIR}" \
        -mindepth 2 \
        -maxdepth 2 \
        -type f \
        -name Dockerfile \
        -print0 | sort -z
)

((${#dockerfiles[@]} > 0)) || fail "nenhum Dockerfile encontrado em ${SERVICES_DIR}."

# Remove do OCIR os recursos da versão selecionada e seus repositórios, além
# das referências locais. A função nunca executa build, tag ou push.
remove_images() {
    local dockerfile
    local service_dir
    local service_name
    local local_image
    local remote_image
    local remote_image_uri
    local remote_image_id
    local repository_name
    local repository_id
    local root_compartment_id
    local image_reference

    # Os repositórios deste laboratório são criados no Root Compartment.
    root_compartment_id="$(get_root_compartment_id)"

    [[ -n "${root_compartment_id}" ]] || \
        fail "não foi possível obter o OCID da tenancy para acessar o Root Compartment."

    for dockerfile in "${dockerfiles[@]}"; do
        # Diretório do serviço associado ao Dockerfile encontrado.
        service_dir="$(dirname "${dockerfile}")"

        # Nome usado para identificar o serviço e seu repositório no OCIR.
        service_name="$(basename "${service_dir}")"

        # Referência curta que pode existir no cache local do Docker.
        local_image="${service_name}:${image_tag}"

        # Referência completa que pode existir no cache local após uma tag.
        remote_image="${OCIR_REGISTRY}/${tenancy_namespace}/${repository_prefix}/${service_name}:${image_tag}"

        # URI aceita pelo OCI CLI para localizar a imagem sem o domínio OCIR.
        remote_image_uri="${tenancy_namespace}/${repository_prefix}/${service_name}:${image_tag}"

        echo
        echo "Localizando ${remote_image} no OCIR..."

        # A consulta resolve a referência repositório/versão para o OCID
        # necessário à operação de exclusão do OCI CLI.
        if remote_image_id="$(
            oci artifacts container image lookup \
                --image-uri "${remote_image_uri}" \
                --query data.id \
                --raw-output
        )" && [[ -n "${remote_image_id}" && "${remote_image_id}" != "null" ]]; then
            echo "Excluindo ${remote_image} do OCIR..."

            oci artifacts container image delete \
                --image-id "${remote_image_id}" \
                --force \
                --wait-for-state DELETED
        else
            echo "Aviso: ${remote_image} não foi encontrada no OCIR; continuando."
        fi

        # Nome do repositório no OCIR, sem namespace, domínio ou versão.
        repository_name="${repository_prefix}/${service_name}"

        # OCID do repositório consultado diretamente no Root Compartment.
        repository_id="$(
            oci artifacts container repository list \
                --compartment-id "${root_compartment_id}" \
                --display-name "${repository_name}" \
                --query 'data.items[0].id' \
                --raw-output
        )"

        if [[ -n "${repository_id}" && "${repository_id}" != "null" ]]; then
            # TODO: Verificar se o repositório contém outros artefatos OCI,
            # como Helm charts, antes de permitir sua exclusão automática.
            echo "Excluindo o repositório ${repository_name} do Root Compartment..."
            
            oci artifacts container repository delete \
                --repository-id "${repository_id}" \
                --force \
                --wait-for-state DELETED
        else
            echo "Repositório ${repository_name} não encontrado no Root Compartment; continuando."
        fi

        # Cada referência é verificada separadamente para que uma tag ausente
        # não impeça a remoção da outra tag presente no Docker local.
        for image_reference in "${local_image}" "${remote_image}"; do
            if docker image inspect "${image_reference}" >/dev/null 2>&1; then
                echo "Removendo ${image_reference} do Docker local..."
                docker image rm "${image_reference}"
            else
                echo "Imagem local ${image_reference} não encontrada; continuando."
            fi
        done

    done

    echo
    echo "Remoção das imagens e dos repositórios concluída."
}

# Exibe a configuração efetiva antes do login e dos builds para permitir que
# o operador interrompa rapidamente uma execução configurada incorretamente.
echo "Registry: ${OCIR_REGISTRY}"
echo "Namespace: ${tenancy_namespace}"
echo "Prefixo: ${repository_prefix}"
echo "Versão: ${image_tag}"
echo "Plataforma: ${TARGET_PLATFORM}"
echo "Serviços encontrados: ${#dockerfiles[@]}"
echo

# O modo de remoção termina aqui para garantir que nenhuma imagem seja
# reconstruída ou publicada novamente durante a mesma execução.
if [[ "${remove_local_images}" == true ]]; then
    remove_images
    exit 0
fi

# Reutiliza a credencial registrada pelo Docker para evitar uma nova
# solicitação de senha a cada execução. A presença da chave do registry em
# `auths` também funciona quando o segredo é mantido por um credential store.
if [[ -f "${DOCKER_CONFIG_FILE}" ]] && \
    jq -e --arg registry "${OCIR_REGISTRY}" \
        '(.auths // {}) | has($registry)' \
        "${DOCKER_CONFIG_FILE}" >/dev/null; then
   
    echo "Credencial existente para ${OCIR_REGISTRY} encontrada em ${DOCKER_CONFIG_FILE}."
   
    echo "Reutilizando a autenticação armazenada pelo Docker."
else
    # O Auth Token é solicitado de forma interativa para não ficar exposto no
    # histórico do shell ou na lista de processos do sistema operacional.
    echo "Credencial para ${OCIR_REGISTRY} não encontrada em ${DOCKER_CONFIG_FILE}."
    echo "Autenticando em ${OCIR_REGISTRY}..."
    
    docker login "${OCIR_REGISTRY}" \
        --username "${tenancy_namespace}/${oci_user}"
fi

# Um array evita expansão insegura de strings ao incluir opcionalmente
# `--no-cache` no comando docker build.
build_options=(--platform "${TARGET_PLATFORM}")

if [[ "${no_cache}" == true ]]; then
    build_options+=(--no-cache)
fi

# Cada serviço recebe primeiro uma tag local curta. Em seguida, a mesma imagem
# recebe a referência completa exigida pelo OCIR e é publicada no repositório
# correspondente ao nome do serviço.
for dockerfile in "${dockerfiles[@]}"; do
    # Diretório usado como contexto do docker build para o serviço atual.
    service_dir="$(dirname "${dockerfile}")"

    # Nome do serviço derivado do diretório que contém seu Dockerfile.
    service_name="$(basename "${service_dir}")"

    # Referência curta atribuída à imagem no Docker local.
    local_image="${service_name}:${image_tag}"

    # Referência completa exigida para publicar a imagem no OCIR.
    remote_image="${OCIR_REGISTRY}/${tenancy_namespace}/${repository_prefix}/${service_name}:${image_tag}"

    # O diretório do serviço é usado como contexto para respeitar o Dockerfile
    # e o .dockerignore específicos de cada componente.
    echo
    echo "Construindo ${local_image}..."

    docker build \
        "${build_options[@]}" \
        --tag "${local_image}" \
        "${service_dir}"

    echo "Aplicando tag ${remote_image}..."

    docker tag "${local_image}" "${remote_image}"

    echo "Publicando ${remote_image}..."

    docker push "${remote_image}"
done

echo
echo "Build e publicação de ${#dockerfiles[@]} imagens concluídos com sucesso."

exit 0
