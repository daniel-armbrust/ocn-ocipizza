.PHONY: development-infra development development-rebuild build

development-infra:
	@echo "Iniciando os serviços de infraestrutura..."
	docker compose up -d mysql nosql rabbitmq redis object-storage

	@echo "Aguardando os serviços de infraestrutura ficarem disponíveis..."
	./scripts/wait-for-infrastructure.sh

development: development-infra
	@echo "Iniciando todos os serviços da aplicação..."
	docker compose up -d

development-rebuild:
	@echo "Reconstruindo todas as imagens sem utilizar cache..."
	docker compose build --no-cache

	@echo "Iniciando o ambiente completo..."
	$(MAKE) development

build:
	@echo "Construindo todas as imagens sem utilizar cache..."
	docker compose build --no-cache
