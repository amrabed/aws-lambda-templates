# Bedrock Agent

This template demonstrates how to handle Amazon Bedrock Agent events using function-based actions.

## Architecture

1.  **Amazon Bedrock Agent** receives user input.
2.  The Agent determines that a function call is needed based on the user's intent.
3.  The Agent invokes the **AWS Lambda function** with function details and parameters.
4.  The Lambda function processes the request using `BedrockAgentFunctionResolver`.
5.  Results are stored in and retrieved from a **DynamoDB table**.

## Features

- **Function-based Actions**: Uses the `@app.tool()` decorator to expose functions to Bedrock Agents.
- **Automatic Parameter Mapping**: Maps Bedrock Agent parameters directly to Python function arguments.
- **Type Safety**: Uses Pydantic models for data validation and camelCase alias conversion.
- **Observability**: Integrated with AWS Lambda Powertools for logging, tracing, and metrics.

## Usage

### Define Tools

Use the `@app.tool()` decorator to define tools that the agent can call:

```python
@app.tool(name="getItem", description="Gets item details by ID")
def get_item(item_id: str) -> dict:
    return handler.get_item(item_id)
```

### Infrastructure

Deploy the stack using:

```bash
make deploy STACK=agent
```
