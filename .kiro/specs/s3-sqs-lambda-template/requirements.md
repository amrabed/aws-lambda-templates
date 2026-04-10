# Requirements Document: S3 → SQS Lambda Template

## Introduction
This feature adds a reusable Lambda function template triggered by S3 object-creation events that forwards processed records to an SQS queue.

## Requirements

### Requirement 1: S3 Event Parsing
- Use Powertools `S3Event` utility.
- Handle zero records gracefully.
- Raise `ValueError` on invalid event shape.

### Requirement 2: Configuration
- Use `pydantic-settings` `BaseSettings`.
- Required `SQS_QUEUE_URL`.
- Default `AWS_DEFAULT_REGION` to `us-east-1`.

### Requirement 3: Infrastructure
- Provide an AWS CDK stack in `infra/stacks/s3.py`.
- Include an S3 bucket with object-creation notifications.
- Include a destination SQS queue.
- Grant necessary permissions.

### Requirement 4: Documentation
- Provide a template description in `docs/template/s3.md`.
- Include it in the templates index.
- Update project README with deployment instructions.
