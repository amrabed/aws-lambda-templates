# Templates
## REST API
A Lambda function that handles GET/POST requests from a REST API and loads/stores records into a DynamoDB table.

- **Trigger**: API Gateway - REST API
- **Destination**: DynamoDB Table

![](diagrams/api.png)

### Code

- **Function code**: [`templates/api`]({{ config.repo_url }}/tree/main/templates/api)
- **Unit tests**: [`tests/api`]({{ config.repo_url }}/tree/main/tests/api)
- **Infra stack**: [`infra/stacks/api.py`]({{ config.repo_url }}/tree/main/infra/stacks/api.py)

### Endpoints

Endpoint | Description | Response codes
--- | --- | ---
`GET /items/{id}` | Retrieve an item by ID | 200, 404, 500
`POST /items` | Create a new item | 201, 422, 500

### Item model

Field | Type | Description
--- | --- | ---
`id` | UUID string | Unique item identifier (auto-generated)
`name` | string | Human-readable item name

### Environment variables

Variable | Description
--- | ---
`TABLE_NAME` | DynamoDB table name
`SERVICE_NAME` | Powertools service name
`METRICS_NAMESPACE` | Powertools metrics namespace


## DynamoDB Stream — Batch Processing
A Lambda function that handles INSERT/MODIFY/DELETE events on items of a source DynamoDB table by batch processing the records and upserting/deleting processed items into/from a destination DynamoDB table.
Partial batch failure reporting is enabled so that individual record failures do not cause the entire batch to be retried. 

- **Trigger**: DynamoDB Streams
- **Destination**: DynamoDB Table

![](diagrams/stream.png)


### Code
- **Function code**: [`templates/stream`]({{ config.repo_url }}/tree/main/templates/stream)
- **Unit tests**: [`tests/stream`]({{ config.repo_url }}/tree/main/tests/stream)
- **Infra stack**: [`infra/stacks/stream.py`]({{ config.repo_url }}/tree/main/infra/stacks/stream.py)

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
