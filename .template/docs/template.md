# ${title_name}
Template description for ${title_name}.

## Architecture

1.  **AWS Lambda function**: Handles events.

![Architecture diagram for ${title_name} showing the data flow between components](diagrams/${name}.png)

## Code

- **Function code**: [`templates/${name}`](/templates/${name})
- **Unit tests**: [`tests/${name}`](/tests/${name})
- **Infra stack**: [`infra/stacks/${name}.py`](/infra/stacks/${name}.py)

## Deployment

Deploy the stack using:

```bash
make deploy STACK=${name}
```

### Data models

Model | Description
--- | ---
`${camel_name}Model` | Description of the data model

### Environment variables

Variable | Description
--- | ---
`TABLE_NAME` | DynamoDB table name
`SERVICE_NAME` | Powertools service name
`METRICS_NAMESPACE` | Powertools metrics namespace
