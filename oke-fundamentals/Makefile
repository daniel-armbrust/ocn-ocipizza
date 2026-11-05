# Serviços de infraestrutura implantados no namespace ocipizza-infra.
INFRA_SERVICES := \
	mysql \
	nosql \
	rabbitmq \
	redis \
	objectstorage \
	mailpit

# Ordem de execução dos bootstraps dos microsserviços OCI Pizza.
BOOTSTRAP_SERVICES := \
	delivery-service \
	notification-service \
	order-service \
	pizza-service \
	user-service

# Ordem de implantação dos microsserviços. O user-service precisa estar
# disponível primeiro porque publica as chaves utilizadas na validação JWT.
APPLICATION_SERVICES := \
	user-service \
	delivery-service \
	notification-service \
	order-service \
	pizza-service \
	admin-service \
	frontend-service

# Namespaces consultados pelo alvo de status do laboratório.
KUBERNETES_NAMESPACES := \
	ocipizza-infra \
	ocipizza-services

# Diretório absoluto deste Makefile, utilizado para localizar os manifestos
# mesmo quando o make for executado a partir da raiz do repositório.
MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
NAMESPACE_DIR := $(MAKEFILE_DIR)kubernetes/namespaces
INFRA_DIR := $(MAKEFILE_DIR)kubernetes/infra
OCIPIZZA_DIR := $(MAKEFILE_DIR)kubernetes/ocipizza
SECRETS_DIR := $(MAKEFILE_DIR)kubernetes/secrets
IMAGE_PULL_SECRET_SCRIPT := $(SECRETS_DIR)/ocir-image-pull-secret-setup.sh
DELETE_IMAGE_PULL_SECRET_SCRIPT := $(SECRETS_DIR)/ocir-image-pull-secret-remove.sh

MAKE_TARGETS := \
	help \
	namespace \
	delete-namespace \
	image-pull-secret \
	delete-image-pull-secret \
	pvc \
	delete-pvc \
	infra \
	delete-infra \
	bootstrap \
	services \
	delete-services \
	ocipizza \
	delete-ocipizza \
	status

.DEFAULT_GOAL := help

.PHONY: \
	oci-pizza-banner \
	help \
	namespace \
	delete-namespace \
	image-pull-secret \
	delete-image-pull-secret \
	pvc \
	delete-pvc \
	infra \
	delete-infra \
	bootstrap \
	services \
	delete-services \
	ocipizza \
	delete-ocipizza \
	status \
	delete-infra-resources

# Impede que as etapas do deploy completo sejam executadas em paralelo.
.NOTPARALLEL: ocipizza delete-ocipizza delete-infra

# Exibe a identidade do projeto antes da execução de qualquer alvo.
oci-pizza-banner:
	@printf '%s\n' ''
	@printf '%s\n' ' ██████╗  ██████╗██╗    ██████╗ ██╗███████╗███████╗ █████╗ '
	@printf '%s\n' '██╔═══██╗██╔════╝██║    ██╔══██╗██║╚══███╔╝╚══███╔╝██╔══██╗'
	@printf '%s\n' '██║   ██║██║     ██║    ██████╔╝██║  ███╔╝   ███╔╝ ███████║'
	@printf '%s\n' '██║   ██║██║     ██║    ██╔═══╝ ██║ ███╔╝   ███╔╝  ██╔══██║'
	@printf '%s\n' '╚██████╔╝╚██████╗██║    ██║     ██║███████╗███████╗██║  ██║'
	@printf '%s\n' ' ╚═════╝  ╚═════╝╚═╝    ╚═╝     ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝'
	@printf '%s\n' ''
	@printf '%s\n' '   OCI Pizza - by Daniel Armbrust (darmbrust@gmail.com)    '
	@printf '%s\n' '                                                           '
	@printf '%s\n' ''

# Todos os alvos públicos dependem do banner para manter a saída padronizada.
$(MAKE_TARGETS): oci-pizza-banner

help: ## Exibe os alvos disponíveis.
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_-]+:.*##/ {printf "  %-24s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@printf '%s\n' ''
	@printf '%s\n' 'Variáveis de ambiente utilizadas:'
	@printf '%s\n' '  REGISTRY        Registry do OCIR (padrão: gru.ocir.io).'
	@printf '%s\n' '  OCI_NAMESPACE   Namespace da tenancy, obtido com: oci os ns get.'
	@printf '%s\n' '  OCI_USERNAME    Usuário OCI usado no imagePullSecret.'
	@printf '%s\n' '  OCI_AUTH_TOKEN  Auth Token OCI; se omitido, será solicitado pelo script.'
	@printf '%s\n' ''
	@printf '%s\n' 'Exemplo:'
	@printf '%s\n' '  export REGISTRY=gru.ocir.io'
	@printf '%s\n' '  export OCI_NAMESPACE=$$(oci os ns get --query data --raw-output)'
	@printf '%s\n' '  export OCI_USERNAME=usuario@example.com'
	@printf '%s\n' '  make ocipizza'

namespace: ## Aplica os namespaces utilizados pelo laboratório.
	@if [ ! -d "$(NAMESPACE_DIR)" ]; then \
		echo "Erro: diretório de namespaces não encontrado: $(NAMESPACE_DIR)" >&2; \
		exit 1; \
	fi
	@echo "Aplicando os namespaces do laboratório..."
	kubectl apply --filename "$(NAMESPACE_DIR)"

delete-namespace: ## Exclui os namespaces utilizados pelo laboratório.
	@if [ ! -d "$(NAMESPACE_DIR)" ]; then \
		echo "Erro: diretório de namespaces não encontrado: $(NAMESPACE_DIR)" >&2; \
		exit 1; \
	fi
	@echo "Excluindo os namespaces e todos os recursos contidos neles..."
	kubectl delete --filename "$(NAMESPACE_DIR)" --ignore-not-found

image-pull-secret: ## Cria ou atualiza o imagePullSecret do OCIR.
	@if [ ! -x "$(IMAGE_PULL_SECRET_SCRIPT)" ]; then \
		echo "Erro: script não encontrado ou sem permissão de execução: $(IMAGE_PULL_SECRET_SCRIPT)" >&2; \
		exit 1; \
	fi
	@echo "Configurando o imagePullSecret do OCIR..."
	"$(IMAGE_PULL_SECRET_SCRIPT)"

delete-image-pull-secret: ## Exclui o imagePullSecret do OCIR.
	@if [ ! -x "$(DELETE_IMAGE_PULL_SECRET_SCRIPT)" ]; then \
		echo "Erro: script não encontrado ou sem permissão de execução: $(DELETE_IMAGE_PULL_SECRET_SCRIPT)" >&2; \
		exit 1; \
	fi
	@echo "Excluindo o imagePullSecret do OCIR..."
	"$(DELETE_IMAGE_PULL_SECRET_SCRIPT)"

pvc: ## Cria os PersistentVolumeClaims dos serviços de infraestrutura.
	@set -e; \
	for service in $(INFRA_SERVICES); do \
		manifest="$(INFRA_DIR)/$$service/pvc.yaml"; \
		if [ -s "$$manifest" ]; then \
			echo "Criando o PVC de $$service..."; \
			kubectl create --filename "$$manifest"; \
		else \
			echo "PVC não definido para $$service; ignorando."; \
		fi; \
	done

delete-pvc: ## Exclui os PersistentVolumeClaims dos serviços de infraestrutura.
	@set -e; \
	for service in $(INFRA_SERVICES); do \
		manifest="$(INFRA_DIR)/$$service/pvc.yaml"; \
		if [ -s "$$manifest" ]; then \
			echo "Excluindo o PVC de $$service..."; \
			kubectl delete --filename "$$manifest" --ignore-not-found; \
		else \
			echo "PVC não definido para $$service; ignorando."; \
		fi; \
	done

infra: pvc ## Cria os PVCs e aplica os Deployments e Services da infraestrutura.
	@set -e; \
	for service in $(INFRA_SERVICES); do \
		deployment="$(INFRA_DIR)/$$service/deployment.yaml"; \
		service_manifest="$(INFRA_DIR)/$$service/service.yaml"; \
		if [ ! -s "$$deployment" ]; then \
			echo "Erro: Deployment não encontrado para $$service: $$deployment" >&2; \
			exit 1; \
		fi; \
		if [ ! -s "$$service_manifest" ]; then \
			echo "Erro: Service não encontrado para $$service: $$service_manifest" >&2; \
			exit 1; \
		fi; \
		echo "Aplicando o Deployment de $$service..."; \
		kubectl apply --filename "$$deployment"; \
		echo "Aplicando o Service de $$service..."; \
		kubectl apply --filename "$$service_manifest"; \
	done

delete-infra-resources:
	@set -e; \
	for service in $(INFRA_SERVICES); do \
		deployment="$(INFRA_DIR)/$$service/deployment.yaml"; \
		service_manifest="$(INFRA_DIR)/$$service/service.yaml"; \
		if [ ! -s "$$deployment" ]; then \
			echo "Erro: Deployment não encontrado para $$service: $$deployment" >&2; \
			exit 1; \
		fi; \
		if [ ! -s "$$service_manifest" ]; then \
			echo "Erro: Service não encontrado para $$service: $$service_manifest" >&2; \
			exit 1; \
		fi; \
		echo "Excluindo o Service de $$service..."; \
		kubectl delete --filename "$$service_manifest" --ignore-not-found; \
		echo "Excluindo o Deployment de $$service..."; \
		kubectl delete --filename "$$deployment" --ignore-not-found; \
	done

delete-infra: delete-infra-resources delete-pvc ## Exclui a infraestrutura e seus PVCs.

services: ## Aplica os Deployments e Services dos microsserviços OCI Pizza.
	@command -v envsubst >/dev/null 2>&1 || { \
		echo "Erro: o comando 'envsubst' não está instalado ou não está no PATH." >&2; \
		exit 1; \
	}
	@test -n "$(REGISTRY)" || { \
		echo "Erro: defina a variável de ambiente REGISTRY." >&2; \
		exit 1; \
	}
	@test -n "$(OCI_NAMESPACE)" || { \
		echo "Erro: defina a variável de ambiente OCI_NAMESPACE." >&2; \
		exit 1; \
	}
	@set -e; \
	for service in $(APPLICATION_SERVICES); do \
		deployment="$(OCIPIZZA_DIR)/$$service/deployment.yaml"; \
		service_manifest="$(OCIPIZZA_DIR)/$$service/service.yaml"; \
		if [ ! -s "$$deployment" ]; then \
			echo "Erro: Deployment não encontrado para $$service: $$deployment" >&2; \
			exit 1; \
		fi; \
		if [ ! -s "$$service_manifest" ]; then \
			echo "Erro: Service não encontrado para $$service: $$service_manifest" >&2; \
			exit 1; \
		fi; \
		echo "Aplicando o Deployment de $$service..."; \
		envsubst '$${REGISTRY} $${OCI_NAMESPACE}' < "$$deployment" | kubectl apply --filename -; \
		echo "Aplicando o Service de $$service..."; \
		kubectl apply --filename "$$service_manifest"; \
	done

delete-services: ## Exclui os Services e Deployments dos microsserviços OCI Pizza.
	@set -e; \
	for service in $(APPLICATION_SERVICES); do \
		deployment="$(OCIPIZZA_DIR)/$$service/deployment.yaml"; \
		service_manifest="$(OCIPIZZA_DIR)/$$service/service.yaml"; \
		if [ ! -s "$$deployment" ]; then \
			echo "Erro: Deployment não encontrado para $$service: $$deployment" >&2; \
			exit 1; \
		fi; \
		if [ ! -s "$$service_manifest" ]; then \
			echo "Erro: Service não encontrado para $$service: $$service_manifest" >&2; \
			exit 1; \
		fi; \
		echo "Excluindo o Service de $$service..."; \
		kubectl delete --filename "$$service_manifest" --ignore-not-found; \
		echo "Excluindo o Deployment de $$service..."; \
		kubectl delete --filename "$$deployment" --ignore-not-found; \
	done

ocipizza: namespace image-pull-secret pvc infra bootstrap services ## Implanta todo o laboratório OCI Pizza.

delete-ocipizza: delete-services delete-infra delete-image-pull-secret delete-namespace ## Exclui todo o laboratório OCI Pizza.

bootstrap: ## Executa os bootstraps dos serviços OCI Pizza.
	@set -e; \
	for service in $(BOOTSTRAP_SERVICES); do \
		script="$(OCIPIZZA_DIR)/$$service/bootstrap.sh"; \
		echo "Executando o bootstrap de $$service..."; \
		(cd "$$(dirname "$$script")" && bash ./bootstrap.sh); \
	done

status: ## Exibe o estado dos recursos do laboratório OCI Pizza.
	@set -e; \
	for namespace in $(KUBERNETES_NAMESPACES); do \
		echo ""; \
		echo "Recursos do namespace $$namespace:"; \
		if kubectl get namespace "$$namespace" >/dev/null 2>&1; then \
			kubectl get deployments,pods,services,persistentvolumeclaims \
				--namespace "$$namespace" \
				--output wide; \
			echo ""; \
			echo "Secrets do projeto no namespace $$namespace:"; \
			if [ "$$namespace" = "ocipizza-infra" ]; then \
				kubectl get secrets ocir-secret \
					--namespace "$$namespace" \
					--ignore-not-found; \
			else \
				kubectl get secrets ocir-secret user-service-jwt \
					--namespace "$$namespace" \
					--ignore-not-found; \
			fi; \
		else \
			echo "Namespace $$namespace não encontrado."; \
		fi; \
	done
