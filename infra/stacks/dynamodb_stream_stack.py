from __future__ import annotations

from aws_cdk import Stack, aws_lambda_event_sources
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_lambda as lambda_
from constructs import Construct


class DynamodbStreamStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs: object) -> None:
        super().__init__(scope, construct_id, **kwargs)

        source_table = dynamodb.Table(
            self,
            "SourceTable",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
        )

        destination_table = dynamodb.Table(
            self,
            "DestinationTable",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )

        function = lambda_.Function(
            self,
            "DynamodbStreamFunction",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="template.scenarios.stream.handler.main",
            code=lambda_.Code.from_asset("."),
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
            aws_lambda_event_sources.DynamoDBEventSource(
                source_table,
                starting_position=lambda_.StartingPosition.TRIM_HORIZON,
            )
        )
