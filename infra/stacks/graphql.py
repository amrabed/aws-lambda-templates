from aws_cdk import Expiration, Stack
from aws_cdk.aws_appsync import (
    ApiKeyConfig,
    AuthorizationConfig,
    AuthorizationType,
    Definition,
    GraphqlApi,
    SchemaFile,
)
from aws_cdk.aws_dynamodb import Attribute, AttributeType, BillingMode, Table
from aws_cdk.aws_lambda import Code, Function, Runtime
from constructs import Construct


class AppSyncDynamodbStack(Stack):
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
            "AppSyncDynamodbFunction",
            runtime=Runtime.PYTHON_3_12,
            handler="templates.graphql.handler.main",
            code=Code.from_asset("."),
            environment={
                "TABLE_NAME": table.table_name,
                "SERVICE_NAME": "appsync-dynamodb",
                "METRICS_NAMESPACE": "AppSyncDynamodb",
            },
        )

        table.grant_read_write_data(function)

        api = GraphqlApi(
            self,
            "AppSyncDynamodbApi",
            name="AppSyncDynamodbApi",
            definition=Definition.from_schema(SchemaFile.from_asset("templates/graphql/schema.graphql")),
            authorization_config=AuthorizationConfig(
                default_authorization=AuthorizationType.API_KEY,
                api_key_config=ApiKeyConfig(expires=Expiration.after_days(365)),
            ),
        )

        data_source = api.add_lambda_data_source("LambdaDataSource", function)

        data_source.create_resolver("GetItemResolver", type_name="Query", field_name="getItem")
        data_source.create_resolver("ListItemsResolver", type_name="Query", field_name="listItems")
        data_source.create_resolver("CreateItemResolver", type_name="Mutation", field_name="createItem")
