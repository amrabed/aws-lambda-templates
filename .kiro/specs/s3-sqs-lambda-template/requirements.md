# Requirements Document

## Introduction

This feature adds a reusable Lambda function template that is triggered by S3 object-creation events and forwards processed records to an SQS queue. The handler follows the existing `templates/` pattern: a `handler.py` entry point, a `settings.py` using `pydantic-settings` `BaseSettings`, and full AWS Lambda Powertools instrumentation (structured logging via `Logger`, tracing via `Tracer`, metrics via `Metrics`, and event parsing via the `S3Event` utility). Fixed string constants use `StrEnum`. Tests use `pytest` + `Hypothesis` with `moto` for AWS mocking.

## Glossary

- **Handler**: The Lambda function entry point (`templates/s3/handler.py`) that receives S3 events and publishes to SQS.
- **Settings**: The Pydantic `BaseSettings` model (`templates/s3/settings.py`) that reads configuration from environment variables.
- **S3Event**: The AWS Lambda Powertools utility class used to parse and iterate over S3 event records.
- **S3Record**: A single object-creation record extracted from an `S3Event`, containing bucket name and object key.
- **ProcessedMessage**: The Pydantic model representing the transformed payload sent to SQS.
- **SQS_Client**: The boto3 SQS client used to publish `ProcessedMessage` instances to the target queue.
- **Logger**: The AWS Lambda Powertools `Logger` instance providing structured JSON log output.
- **Tracer**: The AWS Lambda Powertools `Tracer` instance providing AWS X-Ray tracing.
- **Metrics**: The AWS Lambda Powertools `Metrics` instance publishing custom CloudWatch metrics.
- **DLQ**: Dead-letter queue — an SQS queue that receives messages that the Handler fails to process after exhausting retries.

---

## Requirements

### Requirement 1: S3 Event Parsing

**User Story:** As a platform engineer, I want the Lambda function to reliably parse incoming S3 event payloads, so that each object-creation record is extracted and available for processing.

#### Acceptance Criteria

1. WHEN an S3 event is received, THE Handler SHALL parse it using the Powertools `S3Event` utility and iterate over every record it contains.
2. WHEN an S3 event contains zero records, THE Handler SHALL return without publishing any messages to SQS.
3. IF an S3 event payload cannot be parsed into a valid `S3Event`, THEN THE Handler SHALL log the error via Logger and raise a `ValueError` with a descriptive message.
4. THE Handler SHALL extract the bucket name and object key from each `S3Record` without accessing `os.environ` directly.

---

### Requirement 2: Configuration via Environment Variables

**User Story:** As a platform engineer, I want all runtime configuration to be read from environment variables through a typed Pydantic model, so that the function is portable and testable without code changes.

#### Acceptance Criteria

1. THE Settings SHALL expose a `sqs_queue_url` field of type `str` with no default value, sourced from the `SQS_QUEUE_URL` environment variable.
2. THE Settings SHALL expose a `aws_region` field of type `str` with a default value of `"us-east-1"`, sourced from the `AWS_DEFAULT_REGION` environment variable.
3. THE Settings SHALL expose a `powertools_service_name` field of type `str` with a default value of `"s3-sqs-processor"`, sourced from the `POWERTOOLS_SERVICE_NAME` environment variable.
4. THE Settings SHALL expose a `log_level` field of type `str` with a default value of `"INFO"`, sourced from the `LOG_LEVEL` environment variable.
5. IF the `sqs_queue_url` environment variable is absent or empty, THEN THE Settings SHALL raise a `ValidationError` during instantiation.
6. THE Handler SHALL instantiate Settings once at module load time and reuse the same instance for all invocations.

---

### Requirement 3: Message Processing

**User Story:** As a platform engineer, I want each S3 record to be transformed into a structured `ProcessedMessage`, so that downstream consumers receive a consistent, typed payload.

#### Acceptance Criteria

1. WHEN an `S3Record` is processed, THE Handler SHALL construct a `ProcessedMessage` containing: `bucket` (str), `key` (str), `event_time` (ISO-8601 datetime string), and `source` (a `StrEnum` value identifying the origin system).
2. THE ProcessedMessage SHALL be serialised to JSON using Pydantic's `.model_dump_json()` before being sent to SQS.
3. WHEN serialisation of a `ProcessedMessage` fails, THE Handler SHALL log the error via Logger and skip that record, continuing to process remaining records.
4. THE Handler SHALL add a structured log entry via Logger for each record processed, including `bucket`, `key`, and `event_time` fields.

---

### Requirement 4: SQS Publishing

**User Story:** As a platform engineer, I want each processed message to be published to an SQS queue, so that downstream services can consume the events asynchronously.

#### Acceptance Criteria

1. WHEN a `ProcessedMessage` is ready, THE SQS_Client SHALL publish it to the queue identified by `Settings.sqs_queue_url` using `send_message`.
2. THE Handler SHALL use the `MessageGroupId` attribute when publishing to a FIFO queue, derived from the S3 bucket name.
3. IF `SQS_Client.send_message` raises an exception, THEN THE Handler SHALL log the error via Logger, increment a `publish_failure` Metrics counter, and continue processing remaining records.
4. WHEN all records in an event have been processed, THE Handler SHALL publish a `records_processed` Metrics counter equal to the number of successfully published messages.
5. THE Handler SHALL flush Metrics at the end of every invocation regardless of success or failure.

---

### Requirement 5: Observability

**User Story:** As a platform engineer, I want the Lambda function to emit structured logs, X-Ray traces, and CloudWatch metrics, so that I can monitor and debug it in production.

#### Acceptance Criteria

1. THE Handler SHALL decorate the entry-point function with `@logger.inject_lambda_context` to automatically include Lambda context fields in every log entry.
2. THE Handler SHALL decorate the entry-point function with `@tracer.capture_lambda_handler` to create an X-Ray segment for each invocation.
3. THE Handler SHALL decorate the entry-point function with `@metrics.log_metrics` to ensure metrics are flushed after every invocation.
4. WHILE processing a record, THE Handler SHALL create a Tracer subsegment named `"process_record"` that wraps the per-record processing logic.
5. THE Logger SHALL be initialised with the service name sourced from `Settings.powertools_service_name`.
6. THE Metrics SHALL be initialised with a namespace of `"S3SQSProcessor"` and a service dimension sourced from `Settings.powertools_service_name`.

---

### Requirement 6: Error Handling and Resilience

**User Story:** As a platform engineer, I want the function to handle partial failures gracefully, so that a single bad record does not prevent other records in the same batch from being processed.

#### Acceptance Criteria

1. WHEN processing a batch of S3 records, THE Handler SHALL process each record independently so that a failure on one record does not abort processing of subsequent records.
2. IF an unhandled exception escapes the per-record processing block, THEN THE Handler SHALL log the exception via Logger with `exc_info=True` and continue to the next record.
3. WHEN at least one record in a batch fails to publish, THE Handler SHALL return a response that includes a `batchItemFailures` list containing the identifiers of failed records, following the Lambda partial batch response format.
4. THE Handler SHALL not raise an unhandled exception to the Lambda runtime for per-record failures; only a complete inability to parse the event SHALL propagate as an exception.

---

### Requirement 7: Testing

**User Story:** As a developer, I want a comprehensive test suite for the handler, so that regressions are caught before deployment.

#### Acceptance Criteria

1. THE test suite SHALL mock SQS using `moto` and set required environment variables via `monkeypatch` or `pytest` fixtures — never by modifying `os.environ` directly in test bodies.
2. WHEN a valid S3 event with N records is provided, THE Handler SHALL publish exactly N messages to the mocked SQS queue (property: output count equals input count for valid records).
3. WHEN an S3 event with a mix of valid and invalid records is provided, THE Handler SHALL publish only the valid records and include the invalid record identifiers in `batchItemFailures`.
4. FOR ALL non-empty lists of valid S3 records, processing the same event twice SHALL result in exactly twice as many SQS messages (idempotence is NOT expected; each invocation publishes independently).
5. THE test suite SHALL include a Hypothesis property test verifying that for any list of 1–20 valid S3 records, the number of SQS messages published equals the number of input records.
6. THE test suite SHALL verify that `Settings` raises `ValidationError` when `SQS_QUEUE_URL` is not set.
