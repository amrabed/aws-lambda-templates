# Design Document: Documentation Update

## Overview

This feature updates the project's documentation to accurately reflect the current codebase. The existing `docs/README.md` was written for an earlier version of the template that had a single `project/` folder and no Lambda scenarios. The current codebase has two Lambda scenarios (`templates/api/` and `templates/stream/`), CDK infrastructure stacks, environment variable configuration via pydantic-settings, and a property-based testing setup using Hypothesis. The `mkdocs.yml` navigation also points to a single reference page with an incorrect module path.

The changes are purely documentation — no source code is modified. The deliverables are:

- An updated `docs/README.md`
- An updated `docs/CONTRIBUTING.md`
- An updated `mkdocs.yml`
- A corrected `docs/reference/app.md`
- Three new reference pages: `docs/reference/repository.md`, `docs/reference/api.md`, `docs/reference/stream.md`

## Architecture

The documentation site is built with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) and API reference pages are generated from Python docstrings using [mkdocstrings](https://mkdocstrings.github.io/). The site is configured in `mkdocs.yml` at the repository root.

```
mkdocs.yml                    ← site config, nav, plugins
docs/
  README.md                   ← home page (also the PyPI/GitHub readme)
  CONTRIBUTING.md             ← contributor guide
  reference/
    app.md                    ← ::: templates.app
    repository.md             ← ::: templates.repository
    api.md                    ← ::: templates.api.handler
    stream.md                 ← ::: templates.stream.handler
```

The `mkdocs gh-deploy` command (invoked via `make docs`) builds the site and pushes it to the `gh-pages` branch. `make local` serves it locally for preview.

## Components and Interfaces

### docs/README.md

The primary documentation file. It serves as both the repository landing page and the MkDocs "Overview" home page (referenced in `mkdocs.yml` nav). It must cover:

- Project description (two Lambda scenarios)
- Full tooling list
- Template renaming instructions (`make project`)
- Prerequisites
- Setup commands (all relevant `make` targets)
- API scenario: endpoints, data model, environment variables, response codes
- Stream scenario: event processing, data models, environment variables, partial batch failure
- CDK stacks and deployment commands
- Documentation build commands
- Property-based testing mention
- Accurate project structure tree

### docs/CONTRIBUTING.md

The contributor guide. Requires a small addition documenting where to place new property-based tests.

### mkdocs.yml

Site configuration. Requires:
- `site_name` updated to `AWS Lambda Template - Python`
- `nav` section updated to list all four reference pages under a "Reference" section

### docs/reference/app.md

Fix the incorrect mkdocstrings directive from `aws_lambda_template.app` to `templates.app`.

### docs/reference/repository.md (new)

New reference page with directive `:::  templates.repository`.

### docs/reference/api.md (new)

New reference page with directive `:::  templates.api.handler`.

### docs/reference/stream.md (new)

New reference page with directive `:::  templates.stream.handler`.

## Data Models

This feature involves no code data models. The relevant "data" is the content structure of the documentation files.

The key facts derived from the source code that must appear in the documentation:

**API scenario (`templates/api/`)**
- Handler: `templates.api.handler`
- Endpoints: `GET /items/{id}`, `POST /items`
- Model fields: `id` (UUID string, auto-generated), `name` (string)
- Environment variables: `TABLE_NAME`, `SERVICE_NAME`, `METRICS_NAMESPACE`
- Response codes: 200, 201, 404, 422, 500

**Stream scenario (`templates/stream/`)**
- Handler: `templates.stream.handler`
- Trigger: DynamoDB Streams (INSERT, MODIFY → put to destination; REMOVE → delete from destination)
- Models: `SourceItem`, `DestinationItem`
- Environment variables: `SOURCE_TABLE_NAME`, `DESTINATION_TABLE_NAME`, `SERVICE_NAME`, `METRICS_NAMESPACE`
- Partial batch failure reporting enabled

**CDK stacks (`infra/stacks/`)**
- `ApiGatewayDynamodbStack` → `make deploy STACK=api`
- `DynamodbStreamStack` → `make deploy STACK=stream`
- Entry point: `infra/app.py`
- Optional: `AWS_PROFILE`

**Makefile targets to document**
- `make project NAME=... DESCRIPTION=... AUTHOR=... EMAIL=... GITHUB=... [SOURCE=...]`
- `make install`, `make precommit`, `make venv`, `make lint`, `make test`
- `make deploy STACK=<api|stream> [AWS_PROFILE=...]`
- `make destroy STACK=<api|stream> [AWS_PROFILE=...]`
- `make docs`, `make local`

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: README contains all required tooling names

*For any* tool listed in the requirements (Poetry, Click, pytest, coverage, ruff, pyright, pre-commit, GitHub Actions, Dependabot, Dev Containers, MkDocs, mkdocstrings, Docker, AWS CDK, AWS Lambda Powertools), the README file content should contain that tool's name.

**Validates: Requirements 1.2**

### Property 2: README does not reference the removed project/ folder

*For any* occurrence search of the string `project/` in the README, the result should be empty — the README must not contain any reference to the old `project/` directory.

**Validates: Requirements 1.4**

### Property 3: README contains all required Makefile target names

*For any* Makefile target that the requirements mandate be documented (`install`, `precommit`, `venv`, `lint`, `test`, `deploy`, `destroy`, `project`, `docs`, `local`), the README should contain that target name, and each such target should also exist in the Makefile.

**Validates: Requirements 2.2, 2.3, 2.4, 2.5, 2.6, 5.2, 5.3, 8.1, 9.2**

### Property 4: README contains all required endpoint strings

*For any* HTTP endpoint defined in the API scenario handler (`GET /items/{id}`, `POST /items`), the README should contain a string representation of that endpoint.

**Validates: Requirements 3.2**

### Property 5: README contains all required environment variable names

*For any* environment variable required by either Lambda scenario (`TABLE_NAME`, `SERVICE_NAME`, `METRICS_NAMESPACE`, `SOURCE_TABLE_NAME`, `DESTINATION_TABLE_NAME`), the README should contain that variable name.

**Validates: Requirements 3.4, 4.2**

### Property 6: README contains all required HTTP response codes

*For any* HTTP response code returned by the API scenario (200, 201, 404, 422, 500), the README should contain that status code.

**Validates: Requirements 3.5**

### Property 7: README contains all required data model field names

*For any* data model field documented in the requirements (`id`, `name` for `Item`; `id`, `name` for `SourceItem` and `DestinationItem`), the README should contain that field name alongside its model.

**Validates: Requirements 3.3, 4.4**

### Property 8: All reference pages exist with correct mkdocstrings directives

*For any* module that requires a reference page (`templates.app`, `templates.repository`, `templates.api.handler`, `templates.stream.handler`), the corresponding file under `docs/reference/` should exist and contain a mkdocstrings directive (`:::`) with the fully-qualified module path.

**Validates: Requirements 6.1, 6.2, 6.3, 6.4, 9.3, 9.4**

### Property 9: mkdocs.yml nav lists all four reference pages under Reference

*For any* reference page that must appear in the nav (`app.md`, `repository.md`, `api.md`, `stream.md`), the `mkdocs.yml` nav section should contain an entry pointing to that page under the "Reference" section.

**Validates: Requirements 6.5**

### Property 10: All file paths referenced in the README exist in the repository

*For any* file or directory path explicitly referenced in the README (e.g., `templates/`, `infra/`, `tests/`, `pyproject.toml`, `Makefile`), that path should exist in the repository.

**Validates: Requirements 1.3, 9.1**

## Error Handling

This feature involves only static documentation files. There are no runtime errors to handle. The main failure modes are:

- **Incorrect module path in a reference page**: mkdocstrings will fail to build the site with a `ModuleNotFoundError`. Mitigation: verify each `:::` directive against the actual package structure before committing.
- **Missing reference page file**: mkdocs will fail to build with a "file not found" error. Mitigation: create all four reference pages as part of this feature.
- **Broken nav entry in mkdocs.yml**: mkdocs will warn or error if a nav entry points to a non-existent file. Mitigation: ensure nav entries match the actual file paths.
- **Stale paths in README**: readers will encounter 404s or missing files. Mitigation: the correctness properties (P3, P10) explicitly check that all referenced paths and targets exist.

## Testing Strategy

This feature updates static documentation files. The testing approach is therefore document-content validation rather than unit or integration testing of executable code.

### Unit Tests (example-based)

Specific examples that verify concrete content requirements:

- README contains the string `API_Scenario` or equivalent description
- README does not contain the string `project/`
- README contains a `make project` example invocation with placeholder values
- `docs/reference/app.md` contains `:::  templates.app` (not `aws_lambda_template.app`)
- `mkdocs.yml` `site_name` equals `AWS Lambda Template - Python`
- CONTRIBUTING.md contains guidance on placing property-based tests

### Property-Based Tests (Hypothesis)

The project uses [Hypothesis](https://hypothesis.readthedocs.io) for property-based testing. For this documentation feature, the properties are validated by parameterised pytest tests (iterating over lists of required strings) rather than random generation, since the inputs are finite known sets. Each test is tagged with its design property reference.

**Property test configuration**: minimum 1 iteration per parameterised case (inputs are deterministic lists, not random). Each test references its design property via a comment tag.

Tag format: `# Feature: documentation-update, Property {N}: {property_text}`

**Tests to implement**:

- `test_readme_contains_all_tools` — iterates over the required tool list, asserts each appears in README content. *(Property 1)*
- `test_readme_no_project_folder_reference` — asserts `project/` not in README. *(Property 2)*
- `test_readme_contains_all_make_targets` — iterates over required target names, asserts each appears in README and in Makefile. *(Property 3)*
- `test_readme_contains_endpoints` — asserts endpoint strings present. *(Property 4)*
- `test_readme_contains_env_vars` — iterates over required env var names. *(Property 5)*
- `test_readme_contains_response_codes` — iterates over required status codes. *(Property 6)*
- `test_readme_contains_model_fields` — iterates over required field names. *(Property 7)*
- `test_reference_pages_exist_with_correct_directives` — iterates over module→file mapping, asserts file exists and contains correct `:::` directive. *(Property 8)*
- `test_mkdocs_nav_contains_all_reference_pages` — parses `mkdocs.yml`, asserts all four reference page paths appear under the Reference nav section. *(Property 9)*
- `test_readme_paths_exist` — iterates over paths referenced in README, asserts each exists on disk. *(Property 10)*

Both unit and property tests live in `tests/` alongside existing tests and follow the same naming conventions.
