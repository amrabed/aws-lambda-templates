# SQS — Batch Processing
A Lambda function that handles SQS messages by batch processing them and storing the processed results into a DynamoDB table.
Partial batch failure reporting is enabled so that individual record failures do not cause the entire batch to be retried.

## Architecture

The template sets up:

1.  **Amazon SQS queue**: Holds the incoming messages to be processed.
2.  **AWS Lambda function**: Processes messages in batches with partial failure reporting.
3.  **Amazon DynamoDB table**: Stores the processed items.

![Architecture diagram showing an SQS queue holding messages that are batch-processed by an AWS Lambda function and stored in a DynamoDB table.](diagrams/sqs.png)

## Code

- **Function code**: [`templates/sqs`](/templates/sqs)
- **Unit tests**: [`tests/sqs`](/tests/sqs)
- **Infra stack**: [`infra/stacks/sqs.py`](/infra/stacks/sqs.py)

## Deployment

Deploy the stack using:

```bash
mise run deploy sqs
```

### Data models

#### SqsMessage
Parsed from the SQS message body.

Field | Type | Description
--- | --- | ---
`id` | string | Unique identifier for the message (1-50 chars)
`content` | string | The main content of the message (1-1000 chars)

#### ProcessedItem
Written to the DynamoDB table.

Field | Type | Description
--- | --- | ---
`id` | string | Unique identifier for the item (partition key, 1-50 chars)
`content` | string | The processed content (1-1000 chars)
`status` | string | Processing status (1-50 chars)

### Environment variables

Variable | Description | Required
--- | --- | ---
`TABLE_NAME` | Destination DynamoDB table name | Yes
`SERVICE_NAME` | Powertools service name | No
`METRICS_NAMESPACE` | Powertools metrics namespace | No
