FRAMEWORK ?= react
API_URL ?= http://127.0.0.1:8080
DOCKER_TAG ?= sherman330turbo/pyp-example

.PHONY: run start start-backend start-frontend build-docker install install-back install-front lint test

# `run` is the target name the hexlet-check grading harness invokes
# (`make -C ./code run`); `start` is kept as an alias because that's what
# README.md documents for local use.
start: run

run: install
	npx concurrently \
		--kill-others-on-fail \
		--names "back,front" \
		--prefix-colors "magenta,cyan" \
		"$(MAKE) start-backend" \
		"$(MAKE) start-frontend FRAMEWORK=$(FRAMEWORK)"

start-backend:
	uv run flask --app src/main --debug run --host 0.0.0.0 --port 8080

start-frontend:
	@if [ "$(FRAMEWORK)" = "react" ]; then \
		API_URL="$(API_URL)" npx start-hexlet-devops-deploy-crud-frontend; \
	else \
		echo "No framework this time"; \
		exit 0; \
	fi

install: install-back install-front

install-back:
	@if command -v uv >/dev/null 2>&1 && [ -f uv.lock ]; then \
		uv sync --extra dev; \
	elif python3 -m pip --version >/dev/null 2>&1; then \
		python3 -m pip install -e ".[dev]"; \
	else \
		echo "Neither pip nor uv is available"; \
		exit 1; \
	fi

install-front:
	npm ci

lint:
	@if command -v uv >/dev/null 2>&1 && [ -f uv.lock ]; then \
		uv run ruff check .; \
	else \
		python3 -m ruff check .; \
	fi

test:
	@if command -v uv >/dev/null 2>&1 && [ -f uv.lock ]; then \
		uv run pytest; \
	else \
		python3 -m pytest; \
	fi
