import os
import sys

from aws_cdk import App

from infra.stacks.agent import BedrockAgentStack
from infra.stacks.api import ApiGatewayDynamodbStack
from infra.stacks.eventbridge import EventBridgeApiCallerStack
from infra.stacks.graphql import AppSyncDynamodbStack
from infra.stacks.s3 import S3SqsStack
from infra.stacks.sqs import SqsLambdaDynamodbStack
from infra.stacks.stream import DynamodbStreamStack

STACK_REGISTRY: dict[str, type] = {
    "agent": BedrockAgentStack,
    "api": ApiGatewayDynamodbStack,
    "eventbridge": EventBridgeApiCallerStack,
    "graphql": AppSyncDynamodbStack,
    "s3": S3SqsStack,
    "sqs": SqsLambdaDynamodbStack,
    "stream": DynamodbStreamStack,
}

stack_name = os.environ.get("STACK")

app = App()

if not stack_name or stack_name == "all":
    for stack_class in STACK_REGISTRY.values():
        stack_class(app, stack_class.__name__)
elif stack_name in STACK_REGISTRY:
    stack_class = STACK_REGISTRY[stack_name]
    stack_class(app, stack_class.__name__)
else:
    sys.exit(f"Error: unknown stack '{stack_name}'. Valid values: all, " + ", ".join(STACK_REGISTRY))

app.synth()
