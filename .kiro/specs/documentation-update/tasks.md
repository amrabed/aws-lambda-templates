# Implementation Plan: Documentation Update

## Overview

Update all documentation files to accurately reflect the current codebase (two Lambda scenarios, CDK stacks, pydantic-settings, Hypothesis testing), fix the broken mkdocstrings directive, add three new reference pages, and write parameterised pytest tests that validate the correctness properties from the design.

## Tasks

- [x] 1. Fix and update mkdocs.yml and reference pages
  - [x] 1.1 Update `mkdocs.yml` site_name and nav
    - Set `site_name` to `AWS Lambda Template - Python`
    - Add all four reference pages under the "Reference" nav section: `reference/app.md`, `reference/repository.md`, `reference/api.md`, `reference/stream.md`
    - _Requirements: 6.5, 6.6_

  - [x] 1.2 Fix `docs/reference/app.md` directive
    - Replace `aws_lambda_template.app` with `templates.app`
    - _Requirements: 6.1, 9.3, 9.4_

  - [x] 1.3 Create `docs/reference/repository.md`
    - Add mkdocstrings directive `:::  templates.repository`
    - _Requirements: 6.2_

  - [x] 1.4 Create `docs/reference/api.md`
    - Add mkdocstrings directive `:::  templates.api.handler`
    - _Requirements: 6.3_

  - [x] 1.5 Create `docs/reference/stream.md`
    - Add mkdocstrings directive `:::  templates.stream.handler`
    - _Requirements: 6.4_

- [x] 2. Update `docs/README.md`
  - [x] 2.1 Rewrite project overview section
    - Describe the project as a Python AWS Lambda template with two scenarios: API_Scenario and Stream_Scenario
    - List all required tooling: Poetry, Click, pytest, coverage, ruff, pyright, pre-commit, GitHub Actions, Dependabot, Dev Containers, MkDocs, mkdocstrings, Docker, AWS CDK, AWS Lambda Powertools
    - Remove all references to the `project/` folder
    - _Requirements: 1.1, 1.2, 1.4_

  - [x] 2.2 Update prerequisites and setup section
    - List prerequisites: Python 3.14+, Poetry, Docker, AWS CDK CLI
    - Document `make install`, `make precommit`, `make venv`, `make lint`, `make test` targets
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [x] 2.3 Add template renaming instructions
    - Document `make project` with all parameters: `NAME`, `DESCRIPTION`, `AUTHOR`, `EMAIL`, `GITHUB`, `SOURCE`
    - State it must be run once after cloning, before other setup steps
    - Include a concrete example invocation with placeholder values
    - _Requirements: 8.1, 8.2, 8.3_

  - [x] 2.4 Add API scenario documentation section
    - Describe API_Scenario: REST API via API Gateway backed by DynamoDB
    - Document endpoints: `GET /items/{id}` and `POST /items`
    - Document `Item` model fields: `id` (UUID string, auto-generated) and `name` (string)
    - Document environment variables: `TABLE_NAME`, `SERVICE_NAME`, `METRICS_NAMESPACE`
    - Document response codes: 200, 201, 404, 422, 500
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 2.5 Add Stream scenario documentation section
    - Describe Stream_Scenario: Lambda triggered by DynamoDB Streams, replicates INSERT/MODIFY, propagates REMOVE as deletes
    - Document partial batch failure reporting
    - Document data models: `SourceItem` and `DestinationItem`
    - Document environment variables: `SOURCE_TABLE_NAME`, `DESTINATION_TABLE_NAME`, `SERVICE_NAME`, `METRICS_NAMESPACE`
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x] 2.6 Add CDK infrastructure and deployment section
    - Document `ApiGatewayDynamodbStack` and `DynamodbStreamStack`
    - Document `make deploy STACK=<api|stream>` and `make destroy STACK=<api|stream>`
    - Document optional `AWS_PROFILE` variable
    - Document CDK entry point `infra/app.py` and `STACK` env var
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 2.7 Add property-based testing and documentation build sections
    - Document Hypothesis for property-based testing alongside pytest
    - Document that `make test` runs both standard and Hypothesis tests
    - Document `make docs` and `make local` targets
    - _Requirements: 7.1, 7.2, 9.2_

  - [x] 2.8 Update project structure tree
    - Replace old tree with one reflecting actual layout: `templates/`, `templates/api/`, `templates/stream/`, `infra/`, `infra/stacks/`, `tests/`, `docs/`, top-level config files
    - Ensure every path referenced in the README exists in the repository
    - _Requirements: 1.3, 9.1_

- [x] 3. Update `docs/CONTRIBUTING.md`
  - [x] 3.1 Add property-based testing guidance
    - Document that new property-based tests go in `tests/` alongside standard pytest tests and follow the same naming conventions
    - _Requirements: 7.3_

- [x] 4. Checkpoint — verify docs build locally
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Write documentation correctness tests
  - [x] 5.1 Create `tests/test_documentation.py` with shared fixtures
    - Add fixtures that read `docs/README.md`, `docs/CONTRIBUTING.md`, `mkdocs.yml`, and `Makefile` content once per session
    - _Requirements: 9.1, 9.2_

  - [ ]* 5.2 Write property test for README tooling coverage
    - **Property 1: README contains all required tooling names**
    - **Validates: Requirements 1.2**

  - [ ]* 5.3 Write property test for removed project/ folder reference
    - **Property 2: README does not reference the removed project/ folder**
    - **Validates: Requirements 1.4**

  - [ ]* 5.4 Write property test for Makefile target coverage
    - **Property 3: README contains all required Makefile target names**
    - **Validates: Requirements 2.2, 2.3, 2.4, 2.5, 2.6, 5.2, 5.3, 8.1, 9.2**

  - [ ]* 5.5 Write property test for API endpoint strings
    - **Property 4: README contains all required endpoint strings**
    - **Validates: Requirements 3.2**

  - [ ]* 5.6 Write property test for environment variable names
    - **Property 5: README contains all required environment variable names**
    - **Validates: Requirements 3.4, 4.2**

  - [ ]* 5.7 Write property test for HTTP response codes
    - **Property 6: README contains all required HTTP response codes**
    - **Validates: Requirements 3.5**

  - [ ]* 5.8 Write property test for data model field names
    - **Property 7: README contains all required data model field names**
    - **Validates: Requirements 3.3, 4.4**

  - [ ]* 5.9 Write property test for reference page directives
    - **Property 8: All reference pages exist with correct mkdocstrings directives**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 9.3, 9.4**

  - [ ]* 5.10 Write property test for mkdocs.yml nav completeness
    - **Property 9: mkdocs.yml nav lists all four reference pages under Reference**
    - **Validates: Requirements 6.5**

  - [ ]* 5.11 Write property test for README path existence
    - **Property 10: All file paths referenced in the README exist in the repository**
    - **Validates: Requirements 1.3, 9.1**

- [x] 6. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests use parameterised pytest (not random generation) since inputs are finite known sets
- Each property test must include a comment tag: `# Feature: documentation-update, Property {N}: {property_text}`
- Test file must end with `if __name__ == "__main__": main()`
