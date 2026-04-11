# SQS — Batch Processing
A Lambda function that handles SQS messages by batch processing them and storing the processed results into a DynamoDB table.
Partial batch failure reporting is enabled so that individual record failures do not cause the entire batch to be retried.

- **Trigger**: SQS Queue
- **Destination**: DynamoDB Table

### Code
- **Function code**: [`templates/sqs`](/templates/sqs)
- **Unit tests**: [`tests/sqs`](/tests/sqs)
- **Infra stack**: [`infra/stacks/sqs.py`](/infra/stacks/sqs.py)

### Data models

Model | Description
--- | ---
`SqsMessage` | Parsed from the SQS message body (`id`, `content`)
`ProcessedItem` | Written to the DynamoDB table (`id`, `content`, `status`)

### Environment variables

Variable | Description
--- | ---
`TABLE_NAME` | Destination DynamoDB table name
`SERVICE_NAME` | Powertools service name
`METRICS_NAMESPACE` | Powertools metrics namespace
