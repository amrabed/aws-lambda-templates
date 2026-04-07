import os
import sys

from aws_cdk import App

from infra.stacks.api import ApiGatewayDynamodbStack
from infra.stacks.stream import DynamodbStreamStack

STACK_REGISTRY: dict[str, type] = {
    "api": ApiGatewayDynamodbStack,
    "stream": DynamodbStreamStack,
}

stack_name = os.environ.get("STACK")

if not stack_name:
    sys.exit("Error: STACK environment variable is not set. Valid values: " + ", ".join(STACK_REGISTRY))

if stack_name not in STACK_REGISTRY:
    sys.exit(f"Error: unknown stack '{stack_name}'. Valid values: " + ", ".join(STACK_REGISTRY))

stack_class = STACK_REGISTRY[stack_name]
app = App()
stack_class(app, stack_class.__name__)
app.synth()
