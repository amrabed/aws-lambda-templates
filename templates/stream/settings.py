from pydantic import Field

from templates.settings import CommonSettings


class Settings(CommonSettings, case_sensitive=False):
    destination_table_name: str = Field(description="Destination DynamoDB table name")
    service_name: str = "dynamodb-stream"
    metrics_namespace: str = "DynamoDBStream"
