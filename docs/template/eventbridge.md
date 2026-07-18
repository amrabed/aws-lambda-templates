# EventBridge — API Caller
A Lambda function triggered by an Amazon EventBridge rule that loads an authentication token from AWS Secrets Manager, calls an external HTTP API, and persists the response to a DynamoDB table.

## Architecture

The template sets up:

1.  **Amazon EventBridge rule**: Triggers the function based on a schedule or event pattern.
2.  **AWS Lambda function**: Loads secrets, calls the external API, and saves the response.
3.  **AWS Secrets Manager**: Securely stores the API authentication token.
4.  **Amazon DynamoDB table**: Persists the API responses.

![Architecture diagram showing an EventBridge rule triggering an AWS Lambda function, which retrieves an API token from Secrets Manager, calls an external API, and saves the response to DynamoDB.](diagrams/eventbridge.png)


## Code
- **Function code**: [`templates/eventbridge`](/templates/eventbridge)
- **Unit tests**: [`tests/eventbridge`](/tests/eventbridge)
- **Infra stack**: [`infra/stacks/eventbridge.py`](/infra/stacks/eventbridge.py)

## Deployment

Deploy the stack using:

```bash
mise run deploy eventbridge
```

### Data models

Model | Description
--- | ---
`EventBridgeEvent` | Incoming EventBridge event payload (`source`, `detail_type`, `detail`)
`ApiResponse` | Response from the external HTTP API (`id`, `message`)
`Settings` | Runtime configuration from environment variables

#### ApiResponse
Written to the DynamoDB table after calling the external API.

Field | Type | Description | Required
--- | --- | --- | ---
`id` | string | Unique identifier of the API response record (1-50 chars) | No
`message` | string | Message returned by the external API (1-1000 chars) | Yes

### Environment variables

Variable | Description | Required | Default
--- | --- | --- | ---
`API_URL` | URL of the external HTTP API to call | Yes | -
`TABLE_NAME` | DynamoDB table name for persisting API responses | Yes | -
`SECRET_NAME` | AWS Secrets Manager secret name holding the API token | Yes | -
`SERVICE_NAME` | Powertools service name | No | `eventbridge`
`METRICS_NAMESPACE` | CloudWatch metrics namespace | No | `EventBridge`
`LOG_LEVEL` | Log level for the Lambda Logger | No | `INFO`
