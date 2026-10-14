INFRA_SERVICES := \
	mysql \
	nosql \
	rabbitmq \
	redis \
	object-storage \
	mailpit

APPLICATION_SERVICES := \
	pizza-service \
	user-service \
	delivery-service \
	order-service \
	notification-service \
	frontend-service \
	admin-service

BOOTSTRAP_SCRIPTS := $(wildcard services/*/bootstrap.sh)

.DEFAULT_GOAL := help

.PHONY: \
	help \
	build \
	rebuild \
	development \
	development-infra \
	development-bootstrap \
	development-services \
	development-rebuild \
	development-logs \
	development-down

help: ## Exibe os alvos disponíveis.
	@echo "Alvos disponíveis:"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_-]+:.*##/ {printf "  %-24s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

development-infra: ## Inicia e aguarda a infraestrutura de desenvolvimento.
	@echo "Iniciando os serviços de infraestrutura..."
	docker compose up -d $(INFRA_SERVICES)

	@echo "Aguardando os serviços de infraestrutura ficarem disponíveis..."
	./scripts/wait-for-infrastructure.sh

development-bootstrap: development-infra ## Executa os bootstraps dos serviços disponíveis.
	@echo "Executando o bootstrap dos serviços disponíveis..."
	@set -e; \
	for script in $(BOOTSTRAP_SCRIPTS); do \
		echo "Executando $$script..."; \
		(cd "$$(dirname "$$script")" && ./bootstrap.sh); \
	done

development-services: ## Inicia somente os serviços da aplicação.
	@echo "Iniciando os serviços da aplicação..."
	docker compose up -d --no-deps $(APPLICATION_SERVICES)

development: development-infra ## Inicia a infraestrutura e os serviços da aplicação.
	$(MAKE) development-services

build: ## Constrói as imagens dos serviços utilizando cache.
	@echo "Construindo as imagens dos serviços..."
	docker compose build $(APPLICATION_SERVICES)

rebuild: ## Reconstrói as imagens dos serviços sem utilizar cache.
	@echo "Reconstruindo as imagens dos serviços sem utilizar cache..."
	docker compose build --no-cache $(APPLICATION_SERVICES)

development-rebuild: rebuild ## Reconstrói os serviços e inicia o ambiente.
	$(MAKE) development

development-logs: ## Acompanha os logs dos serviços da aplicação.
	docker compose logs -f $(APPLICATION_SERVICES)

development-down: ## Encerra o ambiente de desenvolvimento.
	docker compose down

# TODO: Implementar o alvo de lint para validar todos os serviços.
# TODO: Implementar o alvo de testes automatizados para todos os serviços.
# TODO: Implementar os alvos compartilhados com os pipelines de CI/CD.
