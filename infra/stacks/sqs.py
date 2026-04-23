from aws_cdk import Stack
from aws_cdk.aws_dynamodb import Attribute, AttributeType, BillingMode, Table
from aws_cdk.aws_lambda import Code, Function, Runtime
from aws_cdk.aws_lambda_event_sources import SqsEventSource
from aws_cdk.aws_sqs import Queue
from constructs import Construct


class SqsLambdaDynamodbStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        queue = Queue(
            self,
            "SourceQueue",
        )

        table = Table(
            self,
            "DestinationTable",
            partition_key=Attribute(name="id", type=AttributeType.STRING),
            billing_mode=BillingMode.PAY_PER_REQUEST,
        )

        function = Function(
            self,
            "SqsLambdaDynamodbFunction",
            runtime=Runtime.PYTHON_3_14,
            handler="templates.sqs.handler.main",
            code=Code.from_asset("."),
            environment={
                "TABLE_NAME": table.table_name,
                "SERVICE_NAME": "sqs-processor",
                "METRICS_NAMESPACE": "SqsProcessor",
            },
        )

        queue.grant_consume_messages(function)
        table.grant_read_write_data(function)

        function.add_event_source(
            SqsEventSource(
                queue,
                batch_size=10,
                report_batch_item_failures=True,
            )
        )
