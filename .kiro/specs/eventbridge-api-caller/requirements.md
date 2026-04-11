# Requirements Document

## Introduction

This feature adds a new Lambda scenario template called `eventbridge-api-caller`. The template demonstrates a Lambda function triggered by an Amazon EventBridge scheduled rule or event-pattern rule that calls an external HTTP API using an authentication token loaded at runtime from AWS Secrets Manager via `SecretsProvider` from AWS Lambda Powertools `parameters`. The API response is persisted to a DynamoDB table using the shared `Repository` class. The template follows all existing project conventions (Poetry, Pydantic, AWS Lambda Powertools, repository pattern, camelCase aliases, Field descriptions) and is structured identically to the existing `api/` and `stream/` templates.

## Glossary

- **Handler**: The AWS Lambda function entry point module at `templates/eventbridge/handler.py`.
- **SecretClient**: The abstraction layer in `secret_client.py` that owns all calls to AWS Secrets Manager via `SecretsProvider`.
- **ApiClient**: The abstraction layer in `api_client.py` that owns all outbound HTTP calls to the external API.
- **Settings**: The Pydantic-settings class in `settings.py` that reads Lambda environment variables.
- **EventBridgeEvent**: The structured Pydantic model representing the incoming EventBridge event payload.
- **ApiResponse**: The structured Pydantic model representing the response received from the external API.
- **EventBridgeApiCallerStack**: The AWS CDK stack in `infra/stacks/eventbridge.py` that provisions all required AWS resources.
- **Token**: The authentication credential (e.g., API key or Bearer token) retrieved from AWS Secrets Manager and injected into outbound HTTP requests.
- **SecretSource**: AWS Secrets Manager, accessed via `SecretsProvider` from `aws_lambda_powertools.utilities.parameters`.
- **Repository**: The shared DynamoDB abstraction at `templates/repository.py` used to persist API responses.
- **TABLE_NAME**: The DynamoDB table name read from the `TABLE_NAME` environment variable.

---

## Requirements

### Requirement 1: EventBridge Trigger

**User Story:** As a platform engineer, I want the Lambda function to be invoked by Amazon EventBridge, so that I can schedule or react to events without managing polling infrastructure.

#### Acceptance Criteria

1. WHEN an EventBridge rule fires, THE Handler SHALL be invoked with the EventBridge event payload.
2. THE Handler SHALL accept both scheduled-rule events (with `source: "aws.events"`) and custom event-pattern events.
3. IF the incoming event cannot be parsed into an EventBridgeEvent model, THEN THE Handler SHALL log the validation error and return without calling the external API.

---

### Requirement 2: Token Loading from External Secret Source

**User Story:** As a security-conscious engineer, I want the authentication token to be loaded from AWS Secrets Manager at runtime, so that credentials are never hard-coded or stored in environment variables.

#### Acceptance Criteria

1. WHEN the Handler initialises, THE SecretClient SHALL load the Token from AWS Secrets Manager using the secret name identified by the environment variable `SECRET_NAME`.
2. THE SecretClient SHALL use `SecretsProvider` from `aws_lambda_powertools.utilities.parameters` for all AWS Secrets Manager interactions.
3. IF the SecretSource is unavailable or returns an error, THEN THE Handler SHALL log the error and raise an exception to signal a Lambda invocation failure.

---

### Requirement 3: External HTTP API Call

**User Story:** As a platform engineer, I want the Lambda function to call an external HTTP API on each invocation, so that I can integrate with third-party services on a schedule or in response to events.

#### Acceptance Criteria

1. WHEN the Handler is invoked, THE ApiClient SHALL send an HTTP request to the URL specified by the environment variable `API_URL`.
2. THE ApiClient SHALL include the Token in the `Authorization` header of every outbound request using the `Bearer` scheme.
3. WHEN the external API returns a 2xx response, THE Handler SHALL parse the response body into an ApiResponse model and log a success metric.
4. IF the external API returns a non-2xx HTTP status code, THEN THE Handler SHALL log the status code and raise an exception to signal a Lambda invocation failure.
5. IF the HTTP request raises a network-level exception (e.g., timeout or connection error), THEN THE Handler SHALL log the exception and re-raise it to signal a Lambda invocation failure.
6. THE ApiClient SHALL use the `urllib.request` standard-library module for all outbound HTTP calls, with no additional third-party HTTP client dependency.

---

### Requirement 4: Observability

**User Story:** As an operations engineer, I want structured logs, distributed traces, and custom metrics emitted on every invocation, so that I can monitor and debug the function in production.

#### Acceptance Criteria

1. THE Handler SHALL emit structured JSON logs using AWS Lambda Powertools `Logger`.
2. THE Handler SHALL emit distributed traces using AWS Lambda Powertools `Tracer`.
3. THE Handler SHALL emit a custom metric `ApiCallSuccess` (count) to the CloudWatch namespace defined by `METRICS_NAMESPACE` on each successful API call.
4. THE Handler SHALL emit a custom metric `ApiCallFailure` (count) to the CloudWatch namespace defined by `METRICS_NAMESPACE` on each failed API call.
5. WHEN the Handler is invoked, THE Logger SHALL inject the Lambda context (request ID, function name) into every log record.

---

### Requirement 5: Configuration via Environment Variables

**User Story:** As a developer, I want all runtime configuration to be read from environment variables, so that the same deployment artifact can be used across environments without code changes.

#### Acceptance Criteria

1. THE Settings SHALL read the following required environment variables: `API_URL`, `SECRET_NAME`, `SERVICE_NAME`, `METRICS_NAMESPACE`, `TABLE_NAME`.
2. IF a required environment variable is absent at Lambda cold-start, THEN THE Settings SHALL raise a validation error that prevents the Handler from initialising.
3. THE Settings class SHALL use `pydantic-settings` `BaseSettings` with each field documented via `Field(description="...")`.

---

### Requirement 6: Data Models

**User Story:** As a developer, I want all event and response payloads to be validated with Pydantic models, so that type safety and schema documentation are enforced at runtime.

#### Acceptance Criteria

1. THE EventBridgeEvent model SHALL validate the incoming EventBridge event and expose at minimum the fields `source`, `detail_type`, and `detail`.
2. THE ApiResponse model SHALL validate the external API response body and expose at minimum a `status` field.
3. THE EventBridgeEvent model SHALL be defined with `populate_by_name=True` and `alias_generator=to_camel`.
4. THE ApiResponse model SHALL be defined with `populate_by_name=True` and `alias_generator=to_camel`.
5. EVERY field in EventBridgeEvent and ApiResponse SHALL be documented with `Field(description="...")`.

---

### Requirement 7: CDK Infrastructure Stack

**User Story:** As a platform engineer, I want a CDK stack that provisions all required AWS resources, so that the template can be deployed with a single command.

#### Acceptance Criteria

1. THE EventBridgeApiCallerStack SHALL provision an AWS Lambda function using `Runtime.PYTHON_3_13` and handler `templates.eventbridge.handler.main`.
2. THE EventBridgeApiCallerStack SHALL provision an EventBridge rule that triggers the Lambda function on a configurable schedule (default: every 5 minutes).
3. THE EventBridgeApiCallerStack SHALL grant the Lambda function `secretsmanager:GetSecretValue` permission on the secret identified by `SECRET_NAME`.
4. THE EventBridgeApiCallerStack SHALL pass `API_URL`, `SECRET_NAME`, `SERVICE_NAME`, `METRICS_NAMESPACE`, and `TABLE_NAME` to the Lambda function as environment variables.
5. THE EventBridgeApiCallerStack SHALL be registered in `infra/app.py` under the key `"eventbridge-api-caller"`.
6. THE EventBridgeApiCallerStack SHALL provision a DynamoDB table with a partition key `id` (String).
7. THE EventBridgeApiCallerStack SHALL grant the Lambda function `dynamodb:PutItem` permission on the DynamoDB table.
8. THE EventBridgeApiCallerStack SHALL pass `TABLE_NAME` to the Lambda function as an environment variable referencing the provisioned DynamoDB table name.

---

### Requirement 8: Unit Tests

**User Story:** As a developer, I want a comprehensive unit-test suite, so that I can verify handler behaviour without deploying to AWS.

#### Acceptance Criteria

1. THE test suite SHALL cover: successful invocation (token loaded, API called, success metric emitted, DynamoDB write performed), secret loading failure, API non-2xx response, API network exception, invalid EventBridge event payload, and DynamoDB write failure (`repository.put_item` raises → handler re-raises, `ApiCallFailure` emitted).
2. THE test suite SHALL mock the SecretClient and ApiClient instances on the handler module rather than patching boto3 or urllib directly.
3. THE test suite SHALL use `pytest` with `pytest-mock` and `monkeypatch` for all mocking, consistent with existing test conventions.
4. EVERY test file SHALL end with the `if __name__ == "__main__": main()` block.
5. THE test suite SHALL set all required environment variables via an `autouse` fixture using `monkeypatch.setenv`.

---

### Requirement 9: Documentation

**User Story:** As a developer, I want a documentation page for the new template, so that I can understand the scenario and find the relevant files quickly.

#### Acceptance Criteria

1. THE documentation SHALL be created at `docs/template/eventbridge.md` and follow the structure of `docs/template/stream.md`.
2. THE documentation SHALL list the trigger, destination, code locations, data models, and environment variables.
3. THE `docs/template/index.md` file SHALL be updated to include a link to the new documentation page.

---

### Requirement 10: Makefile and Deployment Targets

**User Story:** As a developer, I want `make deploy` and `make destroy` to support the new stack, so that I can deploy and tear down the template with the same workflow as existing templates.

#### Acceptance Criteria

1. THE Makefile `STACK_MAP` SHALL include an entry mapping `eventbridge-api-caller` to `EventBridgeApiCallerStack`.
2. WHEN `make deploy STACK=eventbridge-api-caller` is executed, THE Makefile SHALL invoke CDK deploy for `EventBridgeApiCallerStack`.
3. WHEN `make destroy STACK=eventbridge-api-caller` is executed, THE Makefile SHALL invoke CDK destroy for `EventBridgeApiCallerStack`.

---

### Requirement 11: DynamoDB Persistence

**User Story:** As a platform engineer, I want the API response to be persisted to a DynamoDB table, so that I have a durable record of each invocation's result.

#### Acceptance Criteria

1. WHEN the Handler receives a successful ApiResponse, THE Handler SHALL call `repository.put_item` to persist the response to DynamoDB.
2. THE Handler SHALL use the shared `Repository` class from `templates/repository.py` for all DynamoDB interactions.
3. THE Repository SHALL be initialised with the table name from the environment variable `TABLE_NAME`.
4. IF `repository.put_item` raises an exception, THEN THE Handler SHALL log the error and raise an exception to signal a Lambda invocation failure.
