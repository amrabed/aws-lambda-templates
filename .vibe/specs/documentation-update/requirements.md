# Requirements Document

## Introduction

The project documentation is outdated and incomplete. The existing `docs/README.md` references a `project/` folder that no longer exists, omits both Lambda scenarios, the CDK infrastructure stacks, environment variable configuration, deployment workflows, and the property-based testing setup. The `mkdocs.yml` navigation only exposes a single reference page that points to a non-existent module. This feature updates all documentation to accurately reflect the current codebase and adds MkDocs reference pages for every documented module.

## Glossary

- **Docs_Site**: The MkDocs-based documentation site built from the `docs/` folder and `mkdocs.yml`.
- **README**: The file at `docs/README.md`, which serves as both the repository landing page and the MkDocs Overview home page.
- **CONTRIBUTING**: The file at `docs/CONTRIBUTING.md`, which describes how to contribute to the project.
- **API_Scenario**: The Lambda scenario under `templates/api/` that exposes a REST API via API Gateway backed by a single DynamoDB table.
- **Stream_Scenario**: The Lambda scenario under `templates/stream/` that consumes a DynamoDB Streams event source and replicates records to a destination DynamoDB table.
- **CDK_Stack**: An AWS CDK stack defined under `infra/stacks/` and deployed via `make deploy STACK=<name>`.
- **Reference_Page**: A MkDocs page under `docs/reference/` that renders API documentation from Python docstrings using mkdocstrings.
- **Makefile_Target**: A named target in the project `Makefile` invoked with `make <target>`.
- **Environment_Variable**: A runtime configuration value read by a Lambda handler through a pydantic-settings `Settings` class.

---

## Requirements

### Requirement 1: Accurate Project Overview

**User Story:** As a developer evaluating this template, I want the README to describe what the project actually contains, so that I can quickly understand its purpose and structure.

#### Acceptance Criteria

1. THE README SHALL describe the project as a Python AWS Lambda template that provides two ready-to-use scenarios: API_Scenario and Stream_Scenario.
2. THE README SHALL list all tooling used by the project (Poetry, Click, pytest, coverage, ruff, pyright, pre-commit, GitHub Actions, Dependabot, Dev Containers, MkDocs, mkdocstrings, Docker, AWS CDK, AWS Lambda Powertools).
3. THE README SHALL include a project structure tree that reflects the actual layout: `templates/`, `templates/api/`, `templates/stream/`, `infra/`, `infra/stacks/`, `tests/`, `docs/`, and top-level configuration files.
4. THE README SHALL NOT reference the `project/` folder, which no longer exists in the repository.

---

### Requirement 2: Setup and Prerequisites

**User Story:** As a new contributor, I want clear setup instructions, so that I can get the project running locally without guessing.

#### Acceptance Criteria

1. THE README SHALL list the prerequisites for local development: Python 3.14+, Poetry, Docker (for Dev Containers), and AWS CDK CLI (for deployment).
2. THE README SHALL document the `make install` Makefile_Target as the command to install all project dependencies.
3. THE README SHALL document the `make precommit` Makefile_Target as the command to install pre-commit hooks.
4. THE README SHALL document the `make venv` Makefile_Target as the command to activate the virtual environment.
5. THE README SHALL document the `make lint` Makefile_Target as the command to format and lint the code.
6. THE README SHALL document the `make test` Makefile_Target as the command to run tests with coverage.

---

### Requirement 3: Lambda Scenario Documentation — API Gateway + DynamoDB

**User Story:** As a developer using this template, I want documentation for the API Gateway + DynamoDB scenario, so that I understand its endpoints, data model, and required configuration.

#### Acceptance Criteria

1. THE README SHALL describe the API_Scenario as a REST API Lambda function integrated with API Gateway and a single DynamoDB table.
2. THE README SHALL document the two HTTP endpoints exposed by the API_Scenario: `GET /items/{id}` and `POST /items`.
3. THE README SHALL document the `Item` data model fields: `id` (UUID string, auto-generated) and `name` (string).
4. THE README SHALL document the three Environment_Variables required by the API_Scenario: `TABLE_NAME`, `SERVICE_NAME`, and `METRICS_NAMESPACE`.
5. THE README SHALL document the HTTP response codes returned by the API_Scenario: 200 (item found), 201 (item created), 404 (item not found), 422 (validation error), and 500 (internal server error).

---

### Requirement 4: Lambda Scenario Documentation — DynamoDB Streams

**User Story:** As a developer using this template, I want documentation for the DynamoDB Streams scenario, so that I understand how it processes stream events and what configuration it requires.

#### Acceptance Criteria

1. THE README SHALL describe the Stream_Scenario as a Lambda function triggered by DynamoDB Streams that replicates INSERT and MODIFY events to a destination table and propagates REMOVE events as deletes.
2. THE README SHALL document the four Environment_Variables required by the Stream_Scenario: `SOURCE_TABLE_NAME`, `DESTINATION_TABLE_NAME`, `SERVICE_NAME`, and `METRICS_NAMESPACE`.
3. THE README SHALL document that the Stream_Scenario uses partial batch failure reporting so that individual record failures do not cause the entire batch to be retried.
4. THE README SHALL document the two data models used by the Stream_Scenario: `SourceItem` (read from the source table stream) and `DestinationItem` (written to the destination table).

---

### Requirement 5: CDK Infrastructure and Deployment

**User Story:** As a developer deploying this template, I want documentation for the CDK stacks and deployment commands, so that I can deploy and tear down infrastructure without reading the source code.

#### Acceptance Criteria

1. THE README SHALL document the two CDK_Stacks: `ApiGatewayDynamodbStack` (deployed with `make deploy STACK=api`) and `DynamodbStreamStack` (deployed with `make deploy STACK=stream`).
2. THE README SHALL document the `make deploy STACK=<api|stream>` Makefile_Target as the command to deploy a CDK_Stack to AWS.
3. THE README SHALL document the `make destroy STACK=<api|stream>` Makefile_Target as the command to destroy a deployed CDK_Stack.
4. THE README SHALL document the optional `AWS_PROFILE` variable that can be passed to `make deploy` and `make destroy` to select a named AWS CLI profile.
5. THE README SHALL document that the CDK entry point is `infra/app.py` and that the `STACK` environment variable selects which CDK_Stack to synthesise.

---

### Requirement 6: Documentation Site Build and Navigation

**User Story:** As a maintainer, I want the MkDocs site to have accurate navigation and working reference pages, so that generated API docs are accessible and correct.

#### Acceptance Criteria

1. THE Docs_Site SHALL include a Reference_Page for `templates.app` at `docs/reference/app.md` with the correct mkdocstrings directive `:::  templates.app`.
2. THE Docs_Site SHALL include a Reference_Page for `templates.repository` at `docs/reference/repository.md`.
3. THE Docs_Site SHALL include a Reference_Page for `templates.api.handler` at `docs/reference/api.md` that documents the API_Scenario handler.
4. THE Docs_Site SHALL include a Reference_Page for `templates.stream.handler` at `docs/reference/stream.md` that documents the Stream_Scenario handler.
5. THE `mkdocs.yml` nav section SHALL list all four Reference_Pages under a "Reference" section.
6. THE `mkdocs.yml` site_name SHALL be updated to reflect the actual project name (`AWS Lambda Template - Python`).

---

### Requirement 7: Property-Based Testing Documentation

**User Story:** As a contributor, I want documentation on the property-based testing setup, so that I know how to write and run Hypothesis tests.

#### Acceptance Criteria

1. THE README SHALL document that the project uses [Hypothesis](https://hypothesis.readthedocs.io) for property-based testing alongside pytest.
2. THE README SHALL document that `make test` runs both standard pytest tests and Hypothesis property-based tests in a single command.
3. THE CONTRIBUTING SHALL document that new property-based tests should be placed in the `tests/` directory alongside standard pytest tests and follow the same naming conventions.

---

### Requirement 8: Template Renaming Instructions

**User Story:** As a developer starting a new project from this template, I want clear instructions for renaming the template, so that I can customise it for my own project without errors.

#### Acceptance Criteria

1. THE README SHALL document the `make project` Makefile_Target with all accepted parameters: `NAME`, `DESCRIPTION`, `AUTHOR`, `EMAIL`, `GITHUB`, and the optional `SOURCE`.
2. THE README SHALL document that `make project` must be run once after cloning, before any other setup steps.
3. THE README SHALL provide a concrete example invocation of `make project` with placeholder values for all parameters.

---

### Requirement 9: Documentation Accuracy and Consistency

**User Story:** As a reader of the documentation, I want all commands, paths, and module names to be accurate, so that I can follow the documentation without encountering errors.

#### Acceptance Criteria

1. WHEN the README references a file path, THE README SHALL use a path that exists in the current repository layout.
2. WHEN the README references a Makefile_Target, THE README SHALL use a target name that exists in the `Makefile`.
3. WHEN a Reference_Page references a Python module with a mkdocstrings directive, THE Docs_Site SHALL use the fully-qualified module path (e.g., `templates.api.handler`) that matches the actual package structure.
4. IF the `docs/reference/app.md` file contains an incorrect module path (currently `aws_lambda_template.app`), THEN THE Docs_Site SHALL replace it with the correct path `templates.app`.
