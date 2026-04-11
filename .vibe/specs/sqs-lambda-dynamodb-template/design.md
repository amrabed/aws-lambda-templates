# Design Document

## Architecture

The SQS to DynamoDB template follows the standard pattern in this repository:

1.  **SQS Trigger**: An SQS queue triggers the Lambda function.
2.  **Lambda Handler**:
    -   Uses `BatchProcessor` for partial batch failure handling.
    -   Uses `Repository` for DynamoDB interactions.
    -   Follows the `Handler` class pattern seen in `stream` template.
3.  **DynamoDB**: Stores the processed items.

## Components

-   `templates/sqs/handler.py`: Main entry point and processing logic.
-   `templates/sqs/models.py`: Pydantic models for SQS messages and DynamoDB items.
-   `templates/sqs/settings.py`: Configuration management.
-   `infra/stacks/sqs.py`: CDK stack defining SQS queue, DynamoDB table, and Lambda function.
