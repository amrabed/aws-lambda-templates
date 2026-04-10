# Design Document: S3 → SQS Lambda Template

## Architecture
- S3 Bucket -> Lambda -> SQS Queue
- Lambda uses a `Handler` class for processing logic.
- SQS interactions are encapsulated in a `Queue` class.
- Data models reside in `models.py`.

## Implementation Details
- `templates/s3/handler.py`: Main entry point and processing logic.
- `templates/s3/models.py`: Pydantic models for processed messages.
- `templates/s3/queue.py`: Wrapper for boto3 SQS client.
- `templates/s3/settings.py`: Configuration management.
- `infra/stacks/s3.py`: CDK infrastructure.
- `docs/template/s3.md`: User documentation.
