.PHONY: help
.PHONY: development-up development-down development-restart
.PHONY: development-infra development-services development-seed
.PHONY: setup-dev test build logs

help:
	@echo ""
	@echo "Comandos de desenvolvimento do OCI Pizza"
	@echo ""
	@echo "Desenvolvimento:"
	@echo "  make development-up"
	@echo "  make development-down"
	@echo "  make development-restart"
	@echo "  make development-logs"
	@echo ""
	@echo "Carga inicial de dados:"
	@echo "  make development-seed"
	@echo ""
	@echo "Validação:"
	@echo "  make test"
	@echo "  make build"
	@echo ""


## Desenvolvimento
development-up: development-infra development-seed development-services

development-infra:
	@echo "Iniciando os serviços de infraestrutura..."
	docker compose up -d mysql nosql rabbitmq redis

	@echo "Aguardando a infraestrutura ficar pronta..."
	./scripts/wait-for-infrastructure.sh

development-services:
	@echo "Iniciando os serviços da aplicação..."
	docker compose up -d

development-down:
	docker compose down

development-restart:
	make development-down
	make development-up

development-logs:
	docker compose logs -f

## Carga inicial de dados
development-seed:
	@echo "Executando a carga inicial de dados..."
	docker compose run --rm seed

## Ambiente Python
setup-dev:
	@if [ ! -d "seed/.venv" ]; then \
		echo "Criando o ambiente virtual da carga inicial de dados..."; \
		python3 -m venv seed/.venv; \
	fi

	@echo "Instalando as dependências da carga inicial de dados..."
	seed/.venv/bin/pip install \
		--upgrade pip

	seed/.venv/bin/pip install \
		-r seed/requirements.txt

## Validação
test:
	docker compose run --rm pizza-service pytest

build:
	docker compose build

force-build:
	docker compose build --no-cache
