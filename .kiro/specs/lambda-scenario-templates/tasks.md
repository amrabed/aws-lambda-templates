# Implementation Plan: lambda-scenario-templates

## Overview

Implement two self-contained Lambda scenario templates (`api_gateway_dynamodb` and `dynamodb_stream`) under `aws_lambda_template/scenarios/`, with CDK stacks under `infra/stacks/` and pytest suites under `tests/scenarios/`.

## Tasks

- [x] 1. Scaffold scenario package structure and install dependencies
  - Create `aws_lambda_template/scenarios/__init__.py`
  - Create empty `__init__.py` files for each scenario directory: `aws_lambda_template/scenarios/api_gateway_dynamodb/` and `aws_lambda_template/scenarios/dynamodb_stream/`
  - Create `tests/scenarios/__init__.py` and subdirectory `__init__.py` files for each scenario
  - Run `poetry add aws-lambda-powertools pydantic-settings boto3 aws-cdk-lib constructs` (and `poetry add --group dev pytest-mock moto` for test dependencies)
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Implement `api_gateway_dynamodb` scenario
  - [x] 2.1 Create `aws_lambda_template/scenarios/api_gateway_dynamodb/settings.py`
    - Define `Settings(BaseSettings)` with fields: `table_name: str`, `service_name: str`, `metrics_namespace: str`
    - Use `SettingsConfigDict(case_sensitive=False)`
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 4.7_

  - [x] 2.2 Create `aws_lambda_template/scenarios/api_gateway_dynamodb/models.py`
    - Define `Item(BaseModel)` with `id: str` and `name: str`
    - _Requirements: 4.3_

  - [x] 2.3 Create `aws_lambda_template/scenarios/api_gateway_dynamodb/handler.py`
    - Instantiate `Settings`, `Logger`, `Tracer`, `Metrics` at module level
    - Create `boto3` DynamoDB resource at module level
    - Implement `APIGatewayRestResolver` with `GET /items/{id}` (200/404) and `POST /items` (201/422/500)
    - Apply `@logger.inject_lambda_context`, `@tracer.capture_lambda_handler`, `@metrics.log_metrics` decorators
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [x] 2.4 Create `aws_lambda_template/scenarios/api_gateway_dynamodb/__init__.py`
    - Export `handler` function
    - _Requirements: 1.3_

  - [x] 2.5 Write unit tests for `api_gateway_dynamodb` handler
    - Create `tests/scenarios/api_gateway_dynamodb/test_handler.py`
    - Use `monkeypatch` to set `TABLE_NAME`, `SERVICE_NAME`, `METRICS_NAMESPACE`, `POWERTOOLS_SERVICE_NAME`, `POWERTOOLS_METRICS_NAMESPACE`
    - Use `pytest-mock` to mock `boto3` DynamoDB calls
    - Cover: successful GET (200), successful POST (201), item not found (404), invalid body (422), DynamoDB error (500)
    - _Requirements: 7.1, 7.2, 7.3, 7.5_

- [x] 3. Implement `dynamodb_stream` scenario
  - [x] 3.1 Create `aws_lambda_template/scenarios/dynamodb_stream/settings.py`
    - Define `Settings(BaseSettings)` with fields: `source_table_name: str`, `destination_table_name: str`, `service_name: str`, `metrics_namespace: str`
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 5.7_

  - [x] 3.2 Create `aws_lambda_template/scenarios/dynamodb_stream/models.py`
    - Define `DestinationItem(BaseModel)` with `id: str` and any additional fields mirroring the source `NewImage`
    - _Requirements: 5.3_

  - [x] 3.3 Create `aws_lambda_template/scenarios/dynamodb_stream/handler.py`
    - Instantiate `Settings`, `Logger`, `Tracer`, `Metrics` at module level
    - Create `boto3` DynamoDB resource at module level
    - Accept `DynamoDBStreamEvent`; iterate records; handle `INSERT`/`MODIFY` (deserialise `NewImage` via `TypeDeserializer`, write to destination), `REMOVE` (delete from destination)
    - On per-record exception: log error, emit `ProcessingError` metric, continue
    - Apply Powertools decorators
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

  - [x] 3.4 Create `aws_lambda_template/scenarios/dynamodb_stream/__init__.py`
    - Export `handler` function
    - _Requirements: 1.3_

  - [x] 3.5 Write unit tests for `dynamodb_stream` handler
    - Create `tests/scenarios/dynamodb_stream/test_handler.py`
    - Use `monkeypatch` for env vars and `pytest-mock` to mock `boto3` calls
    - Cover: INSERT processed, MODIFY processed, REMOVE processed, deserialisation failure (error logged, continues), DynamoDB write failure (error logged, continues)
    - _Requirements: 7.1, 7.2, 7.4, 7.5_

- [x] 4. Checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement CDK stacks
  - [x] 5.1 Create `infra/__init__.py` and `infra/stacks/__init__.py` (if not present)
    - _Requirements: 1.4_

  - [x] 5.2 Create `infra/stacks/api_gateway_dynamodb_stack.py`
    - Define `ApiGatewayDynamodbStack(Stack)` provisioning: `aws_dynamodb.Table` (PAY_PER_REQUEST, partition key `id`), `aws_lambda.Function` pointing to the scenario handler, `aws_apigateway.RestApi` with Lambda proxy integration
    - _Requirements: 4.8_

  - [x] 5.3 Create `infra/stacks/dynamodb_stream_stack.py`
    - Define `DynamodbStreamStack(Stack)` provisioning: source `Table` with `StreamViewType.NEW_AND_OLD_IMAGES`, destination `Table`, `Function` with `DynamoDBEventSource` on the source stream
    - _Requirements: 5.8_

- [x] 6. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Property-based tests are not included here as the logic is primarily I/O and integration-bound; unit tests cover the key correctness properties
- CDK stacks are standalone and independently deployable per requirement 6.3
