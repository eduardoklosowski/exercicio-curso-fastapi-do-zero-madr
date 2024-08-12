# Projeto

srcdir = src
testdir = tests


# Run

.PHONY: run

run:


# Init

.PHONY: init init-python

init: init-python

init-python:
	poetry install --sync


# Format

.PHONY: fmt fmt-python

fmt: fmt-python

fmt-python:
	poetry run ruff check --select I001 --fix $(srcdir) $(testdir)
	poetry run ruff format $(srcdir) $(testdir)


# Lint

.PHONY: lint lint-python lint-poetry lint-ruff-format lint-ruff-check

lint: lint-python

lint-python: lint-poetry lint-ruff-format lint-ruff-check

lint-poetry:
	poetry check --lock

lint-ruff-format:
	poetry run ruff format --diff $(srcdir) $(testdir)

lint-ruff-check:
	poetry run ruff check $(srcdir) $(testdir)


# Test

.PHONY: test test-python

test: test-python

test-python:


# Clean

.PHONY: clean clean-python clean-pycache clean-python-tools dist-clean

clean: clean-python

clean-python: clean-pycache clean-python-tools

clean-pycache:
	find $(srcdir) $(testdir) -name __pycache__ -exec rm -rf {} +
	find $(srcdir) $(testdir) -type d -empty -delete

clean-python-tools:
	rm -rf .ruff_cache

dist-clean: clean
	rm -rf .venv dist
