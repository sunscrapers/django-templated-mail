.PHONY: init build test run-hooks docs update-deps

init:
	uv sync --all-groups

build:
	uv build

test:
	uv run py.test --capture=no --cov-report term-missing --cov-report html --cov=templated_mail tests/
	uv run coverage xml

run-hooks:
	uv run pre-commit run --all-files --show-diff-on-failure

docs:
	uv sync --group docs --inexact
	cd docs && $(MAKE) html SPHINXBUILD="uv run python -msphinx"

update-deps:
	uv lock --upgrade
	uv sync --all-groups
