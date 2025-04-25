# Define the version of the package
VERSION=$(shell poetry version --short)

# Define Python Version
PYTHON_VERSION=3.11

# Define Poetry Version
POETRY_VERSION=1.7.2

# OS-specific package managers
UNAME := $(shell uname)
PACKAGE_MANAGER_MACOS=brew
PACKAGE_MANAGER_UBUNTU=apt-get
PACKAGE_MANAGER_DEBIAN=apt-get

# Check if Python is installed
check-python:
	@if ! command -v python3 > /dev/null 2>&1; then \
		echo "Python3 not found. Installing Python $(PYTHON_VERSION)..."; \
		$(MAKE) install-python; \
	else \
		echo "Python3 is already installed."; \
	fi

# Check if Poetry is installed
check-poetry:
	@if ! command -v poetry > /dev/null 2>&1; then \
		echo "Poetry not found. Installing Poetry $(POETRY_VERSION)..."; \
		$(MAKE) install-poetry; \
	else \
		echo "Poetry is already installed."; \
	fi

# Install Python 3.11
install-python:
	@if [ "$(UNAME)" = "Darwin" ]; then \
		$(PACKAGE_MANAGER_MACOS) install python@$(PYTHON_VERSION); \
	elif [ "$(UNAME)" = "Linux" ]; then \
		$(PACKAGE_MANAGER_UBUNTU) update && $(PACKAGE_MANAGER_UBUNTU) install -y python3.11 python3.11-venv python3.11-dev; \
	fi

# Install Poetry
install-poetry:
	@curl -sSL https://install.python-poetry.org | python3 -

# Run the application
run:
	poetry run python -m subtitle_generator

# Build the docker images
docker-build:
	# Check Buildx version
	docker buildx version
	# Ensure a named builder instance is created and used
	docker buildx create --use --name klingon_builder || docker buildx use klingon_builder
	# Bootstrap the builder to enable multi-platform builds
	docker buildx inspect klingon_builder --bootstrap
	# Perform the multiplatform build
	docker buildx build --platform linux/amd64,linux/arm64 --build-arg BASE_IMAGE=python:3.10-slim -t djh00t/klingon_subtitles:$(VERSION) --push .

# Push the docker images
docker-push:
	# Push Docker images
	docker push djh00t/klingon_subtitles:$(VERSION)

# Setup development environment
setup_dev: check-python check-poetry
	# Set poetry to save venv in project directory
	poetry config virtualenvs.in-project true

	# Make sure lock file is current
	poetry lock

	# Install dependencies
	poetry install

# Setup development environment
setup-dev: check-python check-poetry
	# Set poetry to save venv in project directory
	poetry config virtualenvs.in-project true

	# Make sure lock file is current
	poetry lock

	# Install dependencies
	poetry install

.PHONY: build clean docker-build docker-push setup-dev check-python check-poetry install-python install-poetry publish test
.PHONY: clean install build test lint format publish help

# Variables
PYTHON := python3
POETRY := poetry

# Default target
.DEFAULT_GOAL := help

clean: ## Remove build artifacts and cache files
	@echo "Cleaning up..."
	rm -rf build dist .eggs *.egg-info
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

install: ## Install project dependencies
	@echo "Installing dependencies..."
	$(POETRY) install

build: clean ## Build the project
	@echo "Building the project..."
	$(POETRY) build

test: ## Run tests
	@echo "Running tests..."
	$(POETRY) run pytest

lint: ## Run linter
	@echo "Running linter..."
	$(POETRY) run flake8 subtitle_generator tests

format: ## Format code
	@echo "Formatting code..."
	$(POETRY) run black subtitle_generator tests

publish: build ## Publish to PyPI
	@echo "Publishing to PyPI..."
	$(POETRY) publish

help: ## Display this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
