from __future__ import annotations

from aws_cdk import Stack
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_lambda as lambda_
from constructs import Construct


class ApiGatewayDynamodbStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs: object) -> None:
        super().__init__(scope, construct_id, **kwargs)

        table = dynamodb.Table(
            self,
            "ItemsTable",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )

        function = lambda_.Function(
            self,
            "ApiGatewayDynamodbFunction",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="template.scenarios.api.handler.main",
            code=lambda_.Code.from_asset("."),
            environment={
                "TABLE_NAME": table.table_name,
                "SERVICE_NAME": "api-gateway-dynamodb",
                "METRICS_NAMESPACE": "ApiGatewayDynamodb",
            },
        )

        table.grant_read_write_data(function)

        api = apigateway.RestApi(self, "ApiGatewayDynamodbApi")
        proxy_integration = apigateway.LambdaIntegration(function, proxy=True)
        api.root.add_proxy(
            default_integration=proxy_integration,
            any_method=True,
        )
