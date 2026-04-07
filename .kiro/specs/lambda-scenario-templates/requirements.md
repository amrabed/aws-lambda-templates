# Requirements Document

## Introduction

This feature adds a set of reusable, scenario-based AWS Lambda handler templates to the project. Each scenario provides a working starting point for a common Lambda integration pattern, wired up with AWS Lambda Powertools (logger, tracer, metrics, parameters, event handlers), Pydantic data models, Pydantic-settings environment config, and AWS CDK infrastructure definitions. Developers pick a scenario, get a fully-structured handler, and extend from there.

The initial scenarios are:

1. **REST API Gateway** — API Gateway (HTTP/REST) trigger with DynamoDB as the read/write backend.
2. **DynamoDB Stream** — DynamoDB Streams trigger that processes change records and writes results to a second DynamoDB table.

The template structure is designed to be extensible so that additional scenarios can be added without modifying existing ones.

---

## Glossary

- **Template**: A self-contained directory under `aws_lambda_template/scenarios/` that implements one Lambda integration scenario.
- **Scenario**: A named integration pattern (e.g., `api_gateway_dynamodb`, `dynamodb_stream`).
- **Handler**: The Python function that AWS Lambda invokes as the entry point for a scenario.
- **Settings**: A Pydantic-settings `BaseSettings` subclass that reads environment variables for a scenario.
- **Model**: A Pydantic `BaseModel` subclass representing a domain object (e.g., an item stored in DynamoDB).
- **Powertools**: AWS Lambda Powertools for Python — provides Logger, Tracer, Metrics, Parameters, and event-type utilities.
- **CDK_Stack**: An AWS CDK `Stack` subclass under `infra/` that provisions the AWS resources for a scenario.
- **API_Gateway**: Amazon API Gateway (REST or HTTP API) used as a Lambda trigger.
- **DynamoDB**: Amazon DynamoDB used as a data store.
- **DynamoDB_Stream**: The change-data-capture stream attached to a DynamoDB table, used as a Lambda trigger.
- **Resolver**: The AWS Lambda Powertools `APIGatewayRestResolver` or `APIGatewayHttpResolver` used to route API Gateway requests to handler functions.

---

## Requirements

### Requirement 1: Scenario Directory Structure

**User Story:** As a developer, I want each scenario to live in its own self-contained directory, so that I can copy or reference a single scenario without touching others.

#### Acceptance Criteria

1. THE Template SHALL be located at `aws_lambda_template/scenarios/{scenario_name}/`.
2. THE Template SHALL contain at minimum the following files: `handler.py`, `models.py`, `settings.py`.
3. THE Template SHALL contain an `__init__.py` that exports the Lambda handler function.
4. WHERE a scenario requires AWS infrastructure, THE Template SHALL have a corresponding CDK stack at `infra/stacks/{scenario_name}_stack.py`.
5. THE Template SHALL NOT share mutable state with other scenario directories.

---

### Requirement 2: Shared Powertools Initialisation

**User Story:** As a developer, I want Powertools utilities (Logger, Tracer, Metrics) initialised consistently across all scenarios, so that observability is uniform without duplicating boilerplate.

#### Acceptance Criteria

1. THE Handler SHALL initialise a Powertools `Logger` with the service name read from the scenario's `Settings`.
2. THE Handler SHALL initialise a Powertools `Tracer` with the service name read from the scenario's `Settings`.
3. THE Handler SHALL initialise a Powertools `Metrics` namespace read from the scenario's `Settings`.
4. WHEN the Lambda function is invoked, THE Handler SHALL use the `@logger.inject_lambda_context` decorator to inject request context into every log record.
5. WHEN the Lambda function is invoked, THE Handler SHALL use the `@tracer.capture_lambda_handler` decorator to trace the full invocation.
6. WHEN the Lambda function is invoked, THE Handler SHALL use the `@metrics.log_metrics` decorator to flush metrics after each invocation.

---

### Requirement 3: Environment Configuration via Pydantic-Settings

**User Story:** As a developer, I want all environment-specific values (table names, service name, etc.) loaded through a typed `Settings` class, so that configuration is validated at startup and never scattered as raw `os.environ` calls.

#### Acceptance Criteria

1. THE Settings SHALL be defined as a `pydantic_settings.BaseSettings` subclass in `settings.py` within each scenario directory.
2. THE Settings SHALL declare every environment variable the scenario depends on as a typed field with a description.
3. IF a required environment variable is missing at Lambda cold-start, THEN THE Settings SHALL raise a `ValidationError` before the handler processes any event.
4. THE Handler SHALL instantiate `Settings` once at module level (outside the handler function) to avoid re-parsing on every invocation.

---

### Requirement 4: REST API Gateway + DynamoDB Scenario

**User Story:** As a developer, I want a ready-to-run scenario for an API Gateway REST trigger backed by DynamoDB, so that I have a working CRUD starting point without writing boilerplate.

#### Acceptance Criteria

1. THE Handler SHALL use the Powertools `APIGatewayRestResolver` (or `APIGatewayHttpResolver`) to route incoming API Gateway events to typed route functions.
2. WHEN a `GET /items/{id}` request is received, THE Handler SHALL retrieve the item from DynamoDB and return it as a JSON response with HTTP status 200.
3. WHEN a `POST /items` request is received, THE Handler SHALL validate the request body against the `Item` Pydantic model and write the item to DynamoDB, returning HTTP status 201.
4. IF the requested item does not exist in DynamoDB, THEN THE Handler SHALL return an HTTP 404 response with a descriptive error message.
5. IF the request body fails Pydantic validation, THEN THE Handler SHALL return an HTTP 422 response with the validation error details.
6. IF a DynamoDB operation raises an exception, THEN THE Handler SHALL log the error with Powertools Logger and return an HTTP 500 response.
7. THE Settings FOR this scenario SHALL include: `TABLE_NAME` (str), `SERVICE_NAME` (str), `METRICS_NAMESPACE` (str).
8. THE CDK_Stack FOR this scenario SHALL provision: one DynamoDB table, one Lambda function with the handler, and one API Gateway REST API connected to the Lambda function.

---

### Requirement 5: DynamoDB Stream Trigger Scenario

**User Story:** As a developer, I want a ready-to-run scenario for a DynamoDB Streams trigger that fans out change records to a destination table, so that I have a working event-driven starting point.

#### Acceptance Criteria

1. THE Handler SHALL accept a `DynamoDBStreamEvent` (Powertools event type) as its input.
2. WHEN a DynamoDB stream event is received, THE Handler SHALL iterate over every record in the event.
3. WHEN a record with event name `INSERT` or `MODIFY` is received, THE Handler SHALL deserialise the `NewImage` into the `DestinationItem` Pydantic model and write it to the destination DynamoDB table.
4. WHEN a record with event name `REMOVE` is received, THE Handler SHALL delete the corresponding item from the destination DynamoDB table using the record's key.
5. IF deserialisation of a stream record fails, THEN THE Handler SHALL log the error with Powertools Logger, emit a `ProcessingError` metric, and continue processing the remaining records.
6. IF a DynamoDB write or delete operation fails, THEN THE Handler SHALL log the error with Powertools Logger, emit a `ProcessingError` metric, and continue processing the remaining records.
7. THE Settings FOR this scenario SHALL include: `SOURCE_TABLE_NAME` (str), `DESTINATION_TABLE_NAME` (str), `SERVICE_NAME` (str), `METRICS_NAMESPACE` (str).
8. THE CDK_Stack FOR this scenario SHALL provision: a source DynamoDB table with Streams enabled, a destination DynamoDB table, and a Lambda function with the handler connected to the source table's stream as an event source.

---

### Requirement 6: Extensibility — Adding New Scenarios

**User Story:** As a developer, I want to add a new scenario by following a clear convention, so that the template structure scales without modifying existing scenarios.

#### Acceptance Criteria

1. THE Template structure SHALL be documented so that a developer can add a new scenario by creating a new directory under `aws_lambda_template/scenarios/` and a corresponding CDK stack under `infra/stacks/`.
2. THE existing scenarios SHALL remain unmodified when a new scenario directory is added.
3. WHERE a new scenario shares infrastructure patterns with an existing scenario, THE CDK_Stack SHALL be independently deployable without depending on another scenario's stack.

---

### Requirement 7: Testing

**User Story:** As a developer, I want each scenario to have pytest tests that cover the happy path and key error conditions, so that I can verify correctness and use the tests as living documentation.

#### Acceptance Criteria

1. THE Template SHALL include a `tests/scenarios/{scenario_name}/` directory with at least one test module per scenario.
2. WHEN testing handler functions, THE test suite SHALL use `pytest-mock` and `monkeypatch` to mock AWS SDK (boto3) calls — no real AWS resources SHALL be contacted during tests.
3. WHEN testing the API Gateway scenario, THE test suite SHALL cover: successful GET, successful POST, item-not-found (404), invalid request body (422), and DynamoDB error (500).
4. WHEN testing the DynamoDB Stream scenario, THE test suite SHALL cover: INSERT record processed, MODIFY record processed, REMOVE record processed, deserialisation failure (error logged, processing continues), and DynamoDB write failure (error logged, processing continues).
5. THE test suite SHALL use Powertools `POWERTOOLS_SERVICE_NAME` and `POWERTOOLS_METRICS_NAMESPACE` environment variables set via `monkeypatch` or `pytest` fixtures to avoid Powertools initialisation errors during tests.
