# Projeto

srcdir = src
testdir = tests


# Run

.PHONY: run

run:
	poetry run fastapi dev $(srcdir)/madr/api.py


# Init

.PHONY: init init-settings init-python

init: init-settings init-python

init-settings:
	[ -e .env ] || cp .env.example .env

init-python:
	poetry install --sync


# Format

.PHONY: fmt fmt-python

fmt: fmt-python

fmt-python:
	poetry run ruff check --select I001 --fix $(srcdir) $(testdir)
	poetry run ruff format $(srcdir) $(testdir)


# Lint

.PHONY: lint lint-python lint-poetry lint-ruff-format lint-ruff-check lint-mypy lint-k8s lint-helm

lint: lint-python lint-k8s

lint-python: lint-poetry lint-ruff-format lint-ruff-check lint-mypy

lint-poetry:
	poetry check --lock

lint-ruff-format:
	poetry run ruff format --diff $(srcdir) $(testdir)

lint-ruff-check:
	poetry run ruff check $(srcdir) $(testdir)

lint-mypy:
	poetry run mypy --show-error-context --pretty $(srcdir) $(testsdir)

lint-k8s: lint-helm

lint-helm:
	helm lint chart


# Test

.PHONY: test test-python test-pytest coverage-html

test: test-python

test-python: test-pytest

test-pytest:
	poetry run pytest --cov=madr --cov-report=term-missing --no-cov-on-fail --cov-fail-under=100 $(testdir)

coverage-html: test-pytest
	poetry run coverage html


# Kubernetes

.PHONY: minikube-start minikube-stop minikube-delete minikube-dashboard minikube-run-app minikube-delete-app

minikube-start:
	minikube start --addons=registry,ingress --insecure-registry 192.168.0.0/16

minikube-stop:
	minikube stop

minikube-delete:
	minikube delete

minikube-dashboard:
	minikube dashboard --port=6001

minikube-run-app:
	./scripts/deploy-in-k8s.sh k8s-values.yaml
	kubectl wait deployments/madr-api --for=condition=available --timeout=-1s
	kubectl port-forward service/madr-api 8000:80

minikube-delete-app:
	helm uninstall madr


# Clean

.PHONY: clean clean-python clean-pycache clean-python-tools clean-k8s dist-clean

clean: clean-python clean-coverage clean-k8s

clean-python: clean-pycache clean-python-tools

clean-pycache:
	find $(srcdir) $(testdir) -name __pycache__ -exec rm -rf {} +
	find $(srcdir) $(testdir) -type d -empty -delete

clean-python-tools:
	rm -rf .ruff_cache .mypy_cache .pytest_cache .coverage .coverage.* htmlcov

clean-k8s:
	rm -rf k8s-values.yaml

dist-clean: clean
	rm -rf .env .venv dist
