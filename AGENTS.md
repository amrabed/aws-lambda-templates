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

Coverage is measured with `coverage` and reported to stdout and `coverage.xml`. The source under test is `templates/`.

## Project Structure

```
templates/              # main package
    api/               # API Gateway + DynamoDB scenario
    stream/            # DynamoDB Streams scenario
tests/                 # pytest tests
docs/                  # MkDocs documentation
infra/                 # AWS CDK infrastructure stacks
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

## Coding Conventions

### Field descriptions

Every field in a Pydantic model or pydantic-settings class must be documented using `Field(description="...")`. This makes descriptions machine-readable and visible in generated JSON schemas.

```python
from pydantic import BaseModel, Field

class Item(BaseModel, populate_by_name=True, alias_generator=to_camel):
    id: str = Field(description="Unique item identifier.")
    name: str = Field(description="Human-readable item name.")
```

### camelCase alias convention

All `BaseModel` subclasses must be defined with `populate_by_name=True` and `alias_generator=to_camel` so that JSON payloads can use camelCase while Python attributes use snake_case.

```python
from uuid import uuid4
from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel

class Item(BaseModel, populate_by_name=True, alias_generator=to_camel):
    item_id: str = Field(description="Unique item identifier.", default_factory=str(uuid4()))
    # Accepts {"itemId": "..."} from JSON; attribute is item.item_id
    # model_dump() → {"item_id": ...}
    # model_dump(by_alias=True) → {"itemId": ...}
```

### No `model_config` class attribute

Do not use `model_config = ConfigDict(...)` or `model_config = SettingsConfigDict(...)`. Pass configuration options as keyword arguments to the base class instead.

```python
# Good
class Item(BaseModel, extra="allow", populate_by_name=True, alias_generator=to_camel): ...
class Settings(BaseSettings, case_sensitive=False): ...

# Bad
class Item(BaseModel):
    model_config = ConfigDict(extra="allow")
```

### Repository pattern for DynamoDB access

Each scenario defines a `Repository` class in `repository.py` that owns all `boto3` DynamoDB calls. The `Handler` class calls repository methods rather than calling `boto3` directly. Tests mock the `Repository` instance rather than patching `boto3.resource`.

```python
from boto3 import resource

class Repository:
    def __init__(self, table_name: str) -> None:
        self._table = resource("dynamodb").Table(table_name)

    def get_item(self, item_id: str) -> dict | None:
        return self._table.get_item(Key={"id": item_id}).get("Item")

    def put_item(self, item: dict) -> None:
        self._table.put_item(Item=item)
```

### Import style

Do not add unnecessary imports like `from __future__ import annotations`. Always use explicit `from x import y` form:

```python
from json import dumps, loads
from pytest import fixture, main, raises
from aws_cdk.aws_lambda import Code, Function, Runtime
```

### Test file main block

Every test file must end with:

```python
if __name__ == "__main__":
    main()
```
