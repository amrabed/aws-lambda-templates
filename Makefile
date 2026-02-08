
NAME ?= project
DESCRIPTION ?= Python Project Template
AUTHOR ?= Amr Abed
EMAIL ?= amrabed
GITHUB ?= amrabed
SOURCE ?= $(shell echo ${NAME} | tr '-' '_' | tr '[:upper:]' '[:lower:]')

.PHONY: project
project: # Rename project (run once)
	@if [ -d project ]; then mv project ${SOURCE}; fi
	@sed -i '' 's/^::: project\.app/::: ${SOURCE}\.app/' docs/reference/app.md
	@sed -i '' 's/^repo_name: .*/repo_name: ${GITHUB}\/${NAME}/' mkdocs.yml
	@sed -i '' 's/^repo_url: .*/repo_url: https:\/\/github.com\/${GITHUB}\/${NAME}/' mkdocs.yml
	@sed -i '' 's/^source = \[.*\]/source = \["${SOURCE}"\]/' pyproject.toml
	@sed -i '' 's/^app = "project\.app:main"/app = "${SOURCE}\.app:main"/' pyproject.toml
	@sed -i '' 's/^name = ".*"/name = "${SOURCE}"/' pyproject.toml
	@sed -i '' 's/^description = ".*"/description = "${DESCRIPTION}"/' pyproject.toml
	@sed -i '' 's/^authors = \[.*\]/authors = \["${AUTHOR} <${EMAIL}>"\]/' pyproject.toml
	@sed -i '' 's/^# .*/# ${DESCRIPTION}/' docs/README.md
	@sed -i '' 's/@.*/@${GITHUB}/' .github/CODEOWNERS
	@sed -i '' 's/^github: \[.*\]/github: \[${GITHUB}\]/' .github/FUNDING.yml
	@sed -i '' 's/^patreon: .*/patreon: # Put your Patreon username here/' .github/FUNDING.yml

poetry:  # Install Poetry
	pipx install -f poetry

venv:
	poetry env activate

install: # Install dependencies and project
	poetry install

update: # Update dependencies
	poetry update

precommit: # Install pre-commit hooks
	poetry run pre-commit autoupdate
	poetry run pre-commit install

pre-commit: precommit

lint:
	poetry run ruff check --fix
	poetry run ruff format
	poetry run pyright .

coverage:
	poetry run coverage run -m pytest .
	poetry run coverage report -m
	poetry run coverage xml

test: coverage

.PHONY: docs
docs: # Build and deploy documentation to GitHub pages
	poetry run mkdocs gh-deploy --force

local: # Serve documentation on a local server
	poetry run mkdocs serve

all: poetry install precommit lint test venv