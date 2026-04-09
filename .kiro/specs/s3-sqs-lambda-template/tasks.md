# Implementation Plan: S3 → SQS Lambda Template

## Overview

Implement `templates/s3/` — a reusable Lambda handler that receives S3 object-creation events, transforms each record into a typed `ProcessedMessage`, and publishes it to SQS. Fully instrumented with AWS Lambda Powertools and covered by pytest + Hypothesis property tests.

## Tasks

- [ ] 1. Create module skeleton and settings
  - Create `templates/s3/__init__.py` (empty)
  - Create `templates/s3/settings.py` with `Settings(BaseSettings, case_sensitive=False)` exposing `sqs_queue_url`, `aws_region`, `powertools_service_name`, and `log_level` fields, each annotated with `Field(description="...")`, sourced from the corresponding environment variables
  - Instantiate `settings = Settings()` at module level in `settings.py`
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [~] 2. Implement data models
  - [~] 2.1 Create `EventSource` StrEnum and `ProcessedMessage` Pydantic model in `templates/s3/handler.py` (or a sibling `models.py`)
    - `EventSource(StrEnum)` with value `s3 = "s3"`
    - `ProcessedMessage(BaseModel, populate_by_name=True, alias_generator=to_camel)` with fields: `bucket: str`, `key: str`, `event_time: str`, `source: EventSource` — every field must have `Field(description="...")`
    - _Requirements: 3.1, 3.2_

  - [ ]* 2.2 Write property test for ProcessedMessage serialization round-trip
    - `# Feature: s3-sqs-lambda-template, Property 4: ProcessedMessage serialization round-trip`
    - **Property 4: ProcessedMessage serialization round-trip**
    - **Validates: Requirements 3.1, 3.2**

- [~] 3. Implement handler internals
  - [~] 3.1 Implement `_parse_event(event)` in `handler.py`
    - Wraps `S3Event(data=event)`; raises `ValueError` with a descriptive message on failure
    - _Requirements: 1.1, 1.3_

  - [~] 3.2 Implement `_build_message(record)` in `handler.py`
    - Constructs a `ProcessedMessage` from an `S3Record` (`bucket`, `key`, `event_time`, `source=EventSource.s3`)
    - _Requirements: 3.1, 3.4_

  - [~] 3.3 Implement `_publish(msg, bucket)` in `handler.py`
    - Calls `sqs_client.send_message(QueueUrl=..., MessageBody=msg.model_dump_json(by_alias=True), MessageGroupId=bucket)`
    - Raises on error (caller handles exception)
    - _Requirements: 4.1, 4.2_

  - [ ]* 3.4 Write property test for MessageGroupId equals bucket name
    - `# Feature: s3-sqs-lambda-template, Property 5: MessageGroupId equals bucket name`
    - **Property 5: MessageGroupId equals bucket name**
    - **Validates: Requirements 4.2**

- [~] 4. Implement `lambda_handler` orchestration
  - [~] 4.1 Wire `_parse_event`, `_build_message`, and `_publish` inside `lambda_handler(event, context)`
    - Decorate with `@logger.inject_lambda_context`, `@tracer.capture_lambda_handler`, `@metrics.log_metrics`
    - Wrap per-record logic in a `tracer.provider.in_subsegment("process_record")` block
    - Log structured fields (`bucket`, `key`, `event_time`) per record via Logger
    - Collect `batchItemFailures` (object key as `itemIdentifier`) for any record that fails to build or publish
    - Increment `publish_failure` metric on `send_message` exceptions
    - Publish `records_processed` metric equal to successful publish count
    - Return `{"batchItemFailures": [...]}` at the end of every invocation
    - _Requirements: 1.1, 1.2, 1.4, 3.3, 3.4, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 6.1, 6.2, 6.3, 6.4_

  - [~] 4.2 Initialise module-level Powertools instances and SQS client
    - `logger = Logger(service=settings.powertools_service_name)`
    - `tracer = Tracer()`
    - `metrics = Metrics(namespace="S3SQSProcessor", service=settings.powertools_service_name)`
    - `sqs_client = boto3.client("sqs", region_name=settings.aws_region)`
    - _Requirements: 2.6, 5.5, 5.6_

- [~] 5. Checkpoint — verify module imports cleanly
  - Ensure `from templates.s3.handler import lambda_handler` succeeds with `SQS_QUEUE_URL` set
  - Ensure all tests pass, ask the user if questions arise.

- [~] 6. Write example-based unit tests
  - [ ] 6.1 Create `tests/s3/__init__.py` and `tests/s3/test_handler.py`
    - Use `mock_aws` from `moto` (via a fixture) for SQS mocking — `moto_aws` does not exist in `tests/conftest.py`; define a local `aws_credentials` + `sqs` fixture or use `mock_aws` as a decorator/context manager
    - Use `monkeypatch` to inject `SQS_QUEUE_URL` and other env vars — never modify `os.environ` directly
    - Test: `Settings` defaults are correct
    - Test: `Settings` raises `ValidationError` when `SQS_QUEUE_URL` is absent
    - Test: zero-record event → handler returns, zero SQS messages published
    - Test: single valid record → handler returns empty `batchItemFailures`, one SQS message published
    - Test: `send_message` failure → record appears in `batchItemFailures`, handler does not raise
    - Test: `_build_message` produces correct fields for a concrete `S3Record`
    - _Requirements: 7.1, 7.3, 7.6, 1.2, 6.3_

  - [ ]* 6.2 Write property test for record count preservation
    - `# Feature: s3-sqs-lambda-template, Property 1: Record count preservation`
    - **Property 1: Record count preservation**
    - Use `s3_record_strategy` generating 1–20 valid S3 records
    - **Validates: Requirements 1.1, 7.2, 7.5**

  - [ ]* 6.3 Write property test for invalid event raises ValueError
    - `# Feature: s3-sqs-lambda-template, Property 2: Invalid event raises ValueError`
    - **Property 2: Invalid event raises ValueError**
    - Use `invalid_event_strategy` generating arbitrary dicts lacking S3 event structure
    - **Validates: Requirements 1.3**

  - [ ]* 6.4 Write property test for missing SQS_QUEUE_URL raises ValidationError
    - `# Feature: s3-sqs-lambda-template, Property 3: Missing SQS_QUEUE_URL raises ValidationError`
    - **Property 3: Missing SQS_QUEUE_URL raises ValidationError**
    - **Validates: Requirements 2.5, 7.6**

  - [ ]* 6.5 Write property test for partial batch failure independence
    - `# Feature: s3-sqs-lambda-template, Property 6: Partial batch failure independence`
    - **Property 6: Partial batch failure independence**
    - Mock SQS to fail for a random subset of records; assert non-failing records are published and `batchItemFailures` contains exactly the failed keys
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 7.3**

  - [ ]* 6.6 Write property test for non-idempotent double invocation
    - `# Feature: s3-sqs-lambda-template, Property 7: Non-idempotent double invocation`
    - **Property 7: Non-idempotent double invocation**
    - Invoke handler twice with the same event; assert SQS message count equals 2×N
    - **Validates: Requirements 7.4**

  - [ ]* 6.7 Write property test for records_processed metric equals success count
    - `# Feature: s3-sqs-lambda-template, Property 8: records_processed metric equals success count`
    - **Property 8: records_processed metric equals success count**
    - For N records where M fail, assert emitted `records_processed` value equals N − M
    - **Validates: Requirements 4.4**

- [~] 7. Final checkpoint — ensure all tests pass
  - Run `make test` and confirm all tests in `tests/s3/test_handler.py` pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Property tests require minimum 100 Hypothesis iterations each (`@settings(max_examples=100)`)
- The `.hypothesis/` directory must not be deleted — it stores shrinking examples
- No `os.environ` / `os.getenv` calls are permitted in `handler.py` or `settings.py`
