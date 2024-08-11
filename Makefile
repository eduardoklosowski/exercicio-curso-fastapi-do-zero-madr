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


# Lint

.PHONY: lint lint-python lint-poetry

lint: lint-python

lint-python: lint-poetry

lint-poetry:
	poetry check --lock


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

dist-clean: clean
	rm -rf .venv dist
