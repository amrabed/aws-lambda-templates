from aws_cdk import Stack
from aws_cdk.aws_apigateway import LambdaIntegration, RestApi
from aws_cdk.aws_dynamodb import Attribute, AttributeType, BillingMode, Table
from aws_cdk.aws_lambda import Function, Runtime
from constructs import Construct

from infra.code import get_lambda_code


class ApiGatewayDynamodbStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        table = Table(
            self,
            "ItemsTable",
            partition_key=Attribute(name="id", type=AttributeType.STRING),
            billing_mode=BillingMode.PAY_PER_REQUEST,
        )

        function = Function(
            self,
            "ApiGatewayDynamodbFunction",
            runtime=Runtime.PYTHON_3_14,
            handler="templates.api.handler.main",
            code=get_lambda_code(),
            environment={
                "TABLE_NAME": table.table_name,
                "SERVICE_NAME": "api-gateway-dynamodb",
                "METRICS_NAMESPACE": "ApiGatewayDynamodb",
            },
        )

        table.grant_read_write_data(function)

        api = RestApi(self, "ApiGatewayDynamodbApi")
        proxy_integration = LambdaIntegration(function, proxy=True)
        api.root.add_proxy(
            default_integration=proxy_integration,
            any_method=True,
        )
