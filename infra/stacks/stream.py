from aws_cdk import Stack
from aws_cdk.aws_dynamodb import Attribute, AttributeType, BillingMode, StreamViewType, Table
from aws_cdk.aws_lambda import Code, Function, Runtime, StartingPosition
from aws_cdk.aws_lambda_event_sources import DynamoDBEventSource
from constructs import Construct


class DynamodbStreamStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        source_table = Table(
            self,
            "SourceTable",
            partition_key=Attribute(name="id", type=AttributeType.STRING),
            billing_mode=BillingMode.PAY_PER_REQUEST,
            stream=StreamViewType.NEW_AND_OLD_IMAGES,
        )

        destination_table = Table(
            self,
            "DestinationTable",
            partition_key=Attribute(name="id", type=AttributeType.STRING),
            billing_mode=BillingMode.PAY_PER_REQUEST,
        )

        function = Function(
            self,
            "DynamodbStreamFunction",
            runtime=Runtime.PYTHON_3_13,
            handler="templates.stream.handler.main",
            code=Code.from_asset("."),
            environment={
                "SOURCE_TABLE_NAME": source_table.table_name,
                "DESTINATION_TABLE_NAME": destination_table.table_name,
                "SERVICE_NAME": "dynamodb-stream",
                "METRICS_NAMESPACE": "DynamodbStream",
            },
        )

        source_table.grant_read_data(function)
        destination_table.grant_read_write_data(function)

        function.add_event_source(
            DynamoDBEventSource(
                source_table,
                starting_position=StartingPosition.TRIM_HORIZON,
                report_batch_item_failures=True,
            )
        )
