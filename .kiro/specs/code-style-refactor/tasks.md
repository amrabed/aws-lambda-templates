# Implementation Plan: code-style-refactor

## Overview

Incremental refactor of the `aws_lambda_template` project: rename the package and scenarios, update Pydantic/pydantic-settings idioms, introduce the Repository and Handler patterns, update tests (including property-based tests), and document the new conventions in `AGENTS.md`.

Each task builds on the previous one. No task leaves orphaned code that is not wired into the rest of the codebase.

## Tasks

- [x] 1. Rename base package `aws_lambda_template` → `template`
  - Create `template/` directory with `__init__.py` and `app.py` copied from `aws_lambda_template/`
  - Recreate the `template/scenarios/` sub-package tree (empty `__init__.py` files only; scenario content comes in later tasks)
  - Update `pyproject.toml`: set `name = "template"`, `packages = [{include = "template"}]`, `app = "template.app:main"`, and `source = ["template"]` under `[tool.coverage.run]`
  - Delete the old `aws_lambda_template/` directory tree after all content has been migrated
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Rename scenarios and migrate source files
  - [x] 2.1 Create `template/scenarios/api/` with placeholder `__init__.py`; copy `handler.py`, `models.py`, `settings.py` from `aws_lambda_template/scenarios/api_gateway_dynamodb/`, updating all internal imports to use `template.scenarios.api.*`
  - [x] 2.2 Create `template/scenarios/stream/` with placeholder `__init__.py`; copy `handler.py`, `models.py`, `settings.py` from `aws_lambda_template/scenarios/dynamodb_stream/`, updating all internal imports to use `template.scenarios.stream.*`
  - [x] 2.3 Delete `aws_lambda_template/scenarios/api_gateway_dynamodb/` and `aws_lambda_template/scenarios/dynamodb_stream/` (and the now-empty `aws_lambda_template/` tree if not already removed in task 1)
  - _Requirements: 2.1, 2.2_

- [x] 3. Update Pydantic models to new idioms
  - [x] 3.1 Rewrite `template/scenarios/api/models.py`: replace bare `BaseModel` with `BaseModel, populate_by_name=True, alias_generator=to_camel`; add `Field(description="...")` to every field; remove any `model_config = ConfigDict(...)` attribute
  - [x] 3.2 Rewrite `template/scenarios/stream/models.py`: same idiom changes; preserve `extra="allow"` as a constructor keyword argument (`class DestinationItem(BaseModel, extra="allow", populate_by_name=True, alias_generator=to_camel)`)
  - [x] 3.3 Write property test for Property 1 (field descriptions stored in FieldInfo) and Property 2 (no class-level `model_config`) and Property 3 (camelCase alias config) and Property 4 (alias round-trip) in `tests/test_properties.py`
    - **Property 1: Field descriptions are stored in Field metadata**
    - **Property 2: No class-level `model_config` attribute**
    - **Property 3: All Pydantic models have camelCase alias support**
    - **Property 4: camelCase alias round-trip**
    - **Validates: Requirements 3.1, 3.2, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4, 5.5**
    - Use `hypothesis` (`@given`, `st.sampled_from`, `st.builds`); tag each test with `# Feature: code-style-refactor, Property N: ...`
    - Add `hypothesis` to dev dependencies via `poetry add --group dev hypothesis`
  - _Requirements: 3.1, 3.2, 4.1, 4.3, 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 4. Update pydantic-settings classes
  - [x] 4.1 Rewrite `template/scenarios/api/settings.py`: replace `model_config = SettingsConfigDict(...)` with constructor keyword args (`class Settings(BaseSettings, case_sensitive=False)`); add `Field(description="...")` to every field; remove `SettingsConfigDict` import
  - [x] 4.2 Rewrite `template/scenarios/stream/settings.py`: same changes as 4.1
  - _Requirements: 3.2, 4.2, 4.4_

- [x] 5. Create `repository.py` for each scenario
  - [x] 5.1 Create `template/scenarios/api/repository.py` with a `Repository` class that accepts a DynamoDB table resource and exposes `get_item(item_id: str) -> dict | None` and `put_item(item: dict) -> None`
  - [x] 5.2 Create `template/scenarios/stream/repository.py` with a `Repository` class that accepts a destination table resource and exposes `put_item(item: dict) -> None` and `delete_item(key: dict) -> None`
  - _Requirements: 6.1, 6.2_

- [x] 6. Refactor `api` handler to `Handler` class + `main` entry point
  - [x] 6.1 Rewrite `template/scenarios/api/handler.py`: move all route logic into a `Handler` class (`__init__` accepts `Repository`; `_register_routes`, `_get_item`, `_create_item` as private methods; `handle(event, context)` delegates to `self._app.resolve`); add module-level `main` function that instantiates `Repository(table)` and `Handler(repo)` and calls `handle`; apply Powertools decorators to `main` only
  - [x] 6.2 Update `infra/stacks/api_gateway_dynamodb_stack.py`: change handler string to `template.scenarios.api.handler.main`
  - _Requirements: 6.3, 7.1, 7.2, 7.4, 8.1, 8.2, 8.3, 8.4_

- [x] 7. Refactor `stream` handler to `Handler` class + `main` entry point
  - [x] 7.1 Rewrite `template/scenarios/stream/handler.py`: move all record-processing logic into a `Handler` class (`__init__` accepts `Repository`; `handle(event, context)` iterates records and calls repository methods); add module-level `main` function that instantiates `Repository(destination_table)` and `Handler(repo)` and calls `handle`; apply Powertools decorators to `main` only
  - [x] 7.2 Update `infra/stacks/dynamodb_stream_stack.py`: change handler string to `template.scenarios.stream.handler.main`
  - _Requirements: 6.3, 7.1, 7.3, 7.4, 8.1, 8.2, 8.3, 8.4_

- [x] 8. Checkpoint — ensure all source changes are consistent
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Update `api` scenario tests
  - [x] 9.1 Rename/move `tests/scenarios/api_gateway_dynamodb/` to `tests/scenarios/api/`; update `test_handler.py`: change import to `template.scenarios.api.handler`; update module-cache flush to match `template.scenarios.api`; replace `mocker.patch.object(handler_module, "table")` with a mock `Repository` instance injected via `mocker.patch`; call `handler_module.main` as the entry point; cover all six test cases listed in the design (`test_get_item_found`, `test_post_item_created`, `test_get_item_not_found`, `test_post_item_invalid_body`, `test_get_item_dynamodb_error`, `test_post_item_dynamodb_error`)
  - [x] 9.2 Write unit tests for `Repository` methods in `tests/scenarios/api/test_repository.py` (mock the boto3 table; verify `get_item` and `put_item` call the table with correct arguments)
    - _Requirements: 6.4, 9.3_
  - _Requirements: 9.1, 9.2, 9.4_

- [x] 10. Update `stream` scenario tests
  - [x] 10.1 Rename/move `tests/scenarios/dynamodb_stream/` to `tests/scenarios/stream/`; update `test_handler.py`: change import to `template.scenarios.stream.handler`; update module-cache flush; replace `mocker.patch.object(handler_module, "destination_table")` with a mock `Repository` instance; call `handler_module.main` as the entry point; cover all five test cases (`test_insert_record_calls_put_item`, `test_modify_record_calls_put_item`, `test_remove_record_calls_delete_item`, `test_deserialisation_failure_continues`, `test_dynamodb_write_failure_continues`)
  - [x] 10.2 Write unit tests for `Repository` methods in `tests/scenarios/stream/test_repository.py` (mock the boto3 table; verify `put_item` and `delete_item` call the table correctly)
    - _Requirements: 6.4, 9.3_
  - _Requirements: 9.1, 9.2, 9.5_

- [x] 11. Final checkpoint — ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 12. Update `AGENTS.md` with new conventions
  - Add a "Coding Conventions" section covering: `Field(description="...")` for all Pydantic/pydantic-settings fields; `Handler` class + `main` entry-point pattern; Repository pattern for DynamoDB access; camelCase alias convention (`populate_by_name=True, alias_generator=to_camel`); updated package name (`template`) and scenario names (`api`, `stream`) in all examples and references
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests (task 3.3) validate universal invariants using Hypothesis; run at least 100 iterations per property (Hypothesis default)
- Unit tests validate specific examples and error conditions
