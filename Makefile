.PHONY: help
.PHONY: development-up development-down development-restart
.PHONY: development-infra development-services development-seed
.PHONY: setup-dev test build logs

help:
	@echo ""
	@echo "OCI Pizza Development Commands"
	@echo ""
	@echo "Development:"
	@echo "  make development-up"
	@echo "  make development-down"
	@echo "  make development-restart"
	@echo "  make development-logs"
	@echo ""
	@echo "Seed:"
	@echo "  make development-seed"
	@echo ""
	@echo "Validation:"
	@echo "  make test"
	@echo "  make build"
	@echo ""


## Development
development-up: development-infra development-seed development-services

development-infra:
	@echo "Starting infrastructure services..."
	docker compose up -d mysql nosql rabbitmq

	@echo "Waiting infrastructure readiness..."
	./scripts/wait-for-infrastructure.sh

development-services:
	@echo "Starting application services..."
	docker compose up -d

development-down:
	docker compose down

development-restart:
	make development-down
	make development-up

development-logs:
	docker compose logs -f

## Seed
development-seed:
	@echo "Executing seed process..."
	docker compose run --rm seed

## Python Environment
setup-dev:
	@if [ ! -d "seed/.venv" ]; then \
		echo "Creating seed virtual environment..."; \
		python3 -m venv seed/.venv; \
	fi

	@echo "Installing seed dependencies..."
	seed/.venv/bin/pip install \
		--upgrade pip

	seed/.venv/bin/pip install \
		-r seed/requirements.txt

## Validation
test:
	docker compose run --rm pizza-service pytest

build:
	docker compose build

force-build:
	docker compose build --no-cache
