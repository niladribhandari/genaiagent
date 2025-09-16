.PHONY: help install install-dev test test-unit test-integration lint format type-check clean build docs demo

# Default target
help: ## Show this help message
	@echo "AgenticAI Code Generation System - Development Commands"
	@echo "======================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install the package in production mode
	pip install -e .

install-dev: ## Install the package in development mode with all dependencies
	pip install -e ".[dev,docs]"

# Testing
test: ## Run all tests
	pytest tests/ -v

test-unit: ## Run unit tests only
	pytest tests/ -v -m "unit or not integration"

test-integration: ## Run integration tests only
	pytest tests/ -v -m "integration"

test-coverage: ## Run tests with coverage report
	pytest tests/ --cov=src/agentic --cov-report=html --cov-report=term

# Code Quality
lint: ## Run linting with flake8
	flake8 src/ tests/ examples/

format: ## Format code with black and isort
	black src/ tests/ examples/
	isort src/ tests/ examples/

format-check: ## Check code formatting without making changes
	black --check src/ tests/ examples/
	isort --check-only src/ tests/ examples/

type-check: ## Run type checking with mypy
	mypy src/

# Development
clean: ## Clean build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	python -m build

# Documentation
docs: ## Build documentation
	cd docs && make html

docs-serve: ## Serve documentation locally
	cd docs && python -m http.server 8000

# Demo and Examples
demo: ## Run the AgenticAI demonstration
	cd examples && python demo_agentic.py

demo-verbose: ## Run the demonstration with verbose output
	cd examples && python demo_agentic.py --verbose

example-spring: ## Generate Spring Boot example project
	python src/main_agentic.py \
		--spec ../API-requirements/policy_management_spec.yml \
		--instructions ../InstructionFiles/java_springboot.yml \
		--project generated_examples/spring_boot_policy

# Development Workflow
dev-setup: install-dev ## Complete development setup
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to verify installation"

pre-commit: format lint type-check test ## Run all pre-commit checks
	@echo "All pre-commit checks passed!"

ci: format-check lint type-check test ## Run all CI checks
	@echo "All CI checks passed!"

# Project Management
init-project: ## Initialize new project structure (already done)
	@echo "Project structure already initialized"
	@echo "Current structure:"
	@tree -I '__pycache__|*.pyc|.git|backup' --dirsfirst

status: ## Show project status
	@echo "AgenticAI Code Generation System Status"
	@echo "======================================="
	@echo "Source files:"
	@find src/ -name "*.py" | wc -l | awk '{print "  Python files: " $$1}'
	@find tests/ -name "*.py" | wc -l | awk '{print "  Test files: " $$1}'
	@echo ""
	@echo "Lines of code:"
	@find src/ -name "*.py" -exec wc -l {} + | tail -1 | awk '{print "  Source: " $$1 " lines"}'
	@find tests/ -name "*.py" -exec wc -l {} + | tail -1 | awk '{print "  Tests: " $$1 " lines"}'
	@echo ""
	@echo "Git status:"
	@git status --porcelain | wc -l | awk '{print "  Modified files: " $$1}'

# Quick commands
quick-test: ## Quick test run (just core functionality)
	pytest tests/test_core.py -v

quick-demo: ## Quick demo run with timeout
	timeout 30s python examples/demo_agentic.py || echo "Demo completed or timed out"
