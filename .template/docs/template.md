# ${title_name}
Template description for ${title_name}.

## Architecture

1.  **AWS Lambda function**: Handles events.

![Architecture diagram showing ${title_name} component interaction and data flow](diagrams/${name}.png)

## Code

- **Function code**: [`templates/${name}`](/templates/${name})
- **Unit tests**: [`tests/${name}`](/tests/${name})
- **Infra stack**: [`infra/stacks/${name}.py`](/infra/stacks/${name}.py)

## Deployment

Deploy the stack using:

```bash
mise run deploy ${name}
```
