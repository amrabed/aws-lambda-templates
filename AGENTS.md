# AGENTS.md

This file provides guidance for AI agents working in this repository.

## Project Overview

Python AWS Lambda project template using [Poetry](https://python-poetry.org/) for dependency management, Click for CLI, and pytest for testing.

## Setup

```bash
make install       # install dependencies
make precommit     # install pre-commit hooks
```

## Common Commands

```bash
make lint          # run ruff (check + format) and pyright
make test          # run pytest with coverage
make docs          # build and deploy docs to GitHub Pages
make local         # serve docs locally
```

## Code Style

- Line length: 120 characters (enforced by ruff)
- Linting rules: `E` (pycodestyle errors) and `I` (isort) via ruff
- Type checking: pyright in strict mode
- All code must pass `make lint` before committing (enforced by pre-commit hooks)

## Testing

Tests live in `tests/`. Run with:

```bash
make test
```

Coverage is measured with `coverage` and reported to stdout and `coverage.xml`. The source under test is `aws_lambda_template/`.

## Project Structure

```
aws_lambda_template/   # main package
tests/                 # pytest tests
docs/                  # MkDocs documentation
```

## Renaming the Template

To rename the project from the default `project` name, run:

```bash
make project NAME=my-project DESCRIPTION="My description" AUTHOR="Name" EMAIL=handle GITHUB=username
```

## Dependencies

- Always use Poetry for dependency management (`poetry add <package>`)
- Use Pydantic for data models
- Use Pydantic-settings for environment variable configuration in a `settings.py` file
- Use [AWS Lambda Powertools](https://docs.aws.amazon.com/powertools/python) wherever applicable: logger, tracer, metrics, parameters, event types, event handlers, etc.

## Infrastructure

- Define and deploy infrastructure using AWS CDK under the `infra/` folder

## Testing Guidelines

- Use pytest, not unittest
- Use `pytest` monkeypatch and `pytest-mock` for mocking instead of `unittest.MagicMock`
- Do not cheat! Never modify source code just to make a failing test pass. Fix real bugs in source code and fix incorrect assertions in tests

## Make Targets

Use `make` targets for all common workflows: lint, test, run locally, and deploy. Refer to `docs/README.md` for currently available targets. Add new targets to `Makefile` as needed.

## Notes

- Python 3.12+ required
- Dependencies are managed via `pyproject.toml` and locked in `poetry.lock`
- Do not edit `poetry.lock` directly; use `make update` to update dependencies
