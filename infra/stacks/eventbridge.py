from aws_cdk import Duration, RemovalPolicy, Stack
from aws_cdk.aws_dynamodb import Attribute, AttributeType, BillingMode, Table
from aws_cdk.aws_events import Rule, Schedule
from aws_cdk.aws_events_targets import LambdaFunction
from aws_cdk.aws_lambda import Code, Function, Runtime
from aws_cdk.aws_secretsmanager import Secret
from constructs import Construct


class EventBridgeApiCallerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        table = Table(
            self,
            "EventBridgeApiCallerTable",
            partition_key=Attribute(name="id", type=AttributeType.STRING),
            billing_mode=BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        secret = Secret(self, "EventBridgeApiCallerSecret")

        function = Function(
            self,
            "EventBridgeApiCallerFunction",
            runtime=Runtime.PYTHON_3_13,
            handler="templates.eventbridge.handler.main",
            code=Code.from_asset("."),
            environment={
                "API_URL": "https://api.example.com",
                "SECRET_NAME": secret.secret_name,
                "SERVICE_NAME": "eventbridge-api-caller",
                "METRICS_NAMESPACE": "EventBridgeApiCaller",
                "TABLE_NAME": table.table_name,
            },
        )

        table.grant_write_data(function)
        secret.grant_read(function)

        Rule(
            self,
            "EventBridgeApiCallerRule",
            schedule=Schedule.rate(Duration.minutes(5)),
            targets=[LambdaFunction(function)],
        )
