# DynamoDB Stream — Batch Processing
A Lambda function that handles INSERT/MODIFY/DELETE events on items of a source DynamoDB table by batch processing the records and upserting/deleting processed items into/from a destination DynamoDB table.
Partial batch failure reporting is enabled so that individual record failures do not cause the entire batch to be retried. 

- **Trigger**: DynamoDB Streams
- **Destination**: DynamoDB Table

![](diagrams/stream.png)


## Code

- **Function code**: [`templates/stream`](/templates/stream)
- **Unit tests**: [`tests/stream`](/tests/stream)
- **Infra stack**: [`infra/stacks/stream.py`](/infra/stacks/stream.py)

## Deployment

Deploy the stack using:

```bash
make deploy STACK=stream
```


### Data models

Model | Description
--- | ---
`SourceItem` | Read from the source table stream (`id`, `name`)
`DestinationItem` | Written to the destination table (`id`, `name`)

### Environment variables

Variable | Description
--- | ---
`SOURCE_TABLE_NAME` | Source DynamoDB table name (stream source)
`DESTINATION_TABLE_NAME` | Destination DynamoDB table name
`SERVICE_NAME` | Powertools service name
`METRICS_NAMESPACE` | Powertools metrics namespace
