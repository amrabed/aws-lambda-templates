from aws_cdk import Stack
from aws_cdk.aws_dynamodb import Attribute, AttributeType, BillingMode, Table
from aws_cdk.aws_lambda import Code, Function, Runtime
from constructs import Construct


class BedrockAgentStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        table = Table(
            self,
            "AgentTable",
            partition_key=Attribute(name="id", type=AttributeType.STRING),
            billing_mode=BillingMode.PAY_PER_REQUEST,
        )

        function = Function(
            self,
            "BedrockAgentFunction",
            runtime=Runtime.PYTHON_3_14,
            handler="templates.bedrock_agent.handler.main",
            code=Code.from_asset("."),
            environment={
                "TABLE_NAME": table.table_name,
                "SERVICE_NAME": "bedrock-agent",
                "METRICS_NAMESPACE": "BedrockAgent",
            },
        )

        table.grant_read_write_data(function)
