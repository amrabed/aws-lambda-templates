import os
import sys

from aws_cdk import App

from infra.stacks.api import ApiGatewayDynamodbStack
from infra.stacks.bedrock_agent import BedrockAgentStack
from infra.stacks.eventbridge import EventBridgeApiCallerStack
from infra.stacks.s3 import S3SqsStack
from infra.stacks.sqs import SqsLambdaDynamodbStack
from infra.stacks.stream import DynamodbStreamStack

STACK_REGISTRY: dict[str, type] = {
    "api": ApiGatewayDynamodbStack,
    "bedrock-agent": BedrockAgentStack,
    "eventbridge-api-caller": EventBridgeApiCallerStack,
    "stream": DynamodbStreamStack,
    "s3": S3SqsStack,
    "sqs": SqsLambdaDynamodbStack,
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
