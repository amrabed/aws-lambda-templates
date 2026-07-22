# DynamoDB Stream — Batch Processing
A Lambda function that handles INSERT/MODIFY/DELETE events on items of a source DynamoDB table by batch processing the records and upserting/deleting processed items into/from a destination DynamoDB table.
Partial batch failure reporting is enabled so that individual record failures do not cause the entire batch to be retried. 

## Architecture

The template sets up:

1.  **Source Amazon DynamoDB Stream**: Provides the stream of data events.
2.  **AWS Lambda function**: Batch processes stream records with partial failure reporting.
3.  **Destination Amazon DynamoDB table**: Stores the processed output.

![Architecture diagram showing a DynamoDB Stream capturing changes from a source table and triggering an AWS Lambda function to batch-process and upsert records into a destination DynamoDB table.](diagrams/stream.png)


## Code

- **Function code**: [`templates/stream`](/templates/stream)
- **Unit tests**: [`tests/stream`](/tests/stream)
- **Infra stack**: [`infra/stacks/stream.py`](/infra/stacks/stream.py)

## Deployment

Deploy the stack using:

```bash
mise run deploy stream
```


### Data models

#### SourceItem
Read from the source table stream.

Field | Type | Description | Required
--- | --- | --- | ---
`id` | string | Unique item identifier (1-50 chars) | Yes
`name` | string | Human-readable item name (optional, 1-100 chars) | No

#### DestinationItem
Written to the destination table.

Field | Type | Description | Required
--- | --- | --- | ---
`id` | string | Unique item identifier (1-50 chars) | Yes
`name` | string | Human-readable item name (optional, 1-100 chars) | No

### Environment variables

Variable | Description | Required | Default
--- | --- | --- | ---
`SOURCE_TABLE_NAME` | Source DynamoDB table name (stream source) | Yes | -
`DESTINATION_TABLE_NAME` | Destination DynamoDB table name | Yes | -
`SERVICE_NAME` | Powertools service name | No | `dynamodb-stream`
`METRICS_NAMESPACE` | Powertools metrics namespace | No | `DynamoDBStream`
`LOG_LEVEL` | Log level for the Lambda Logger | No | `INFO`

[← Back to Overview](../README.md)
