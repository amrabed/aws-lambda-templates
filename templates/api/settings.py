from pydantic import Field

from templates.settings import CommonSettings


class Settings(CommonSettings):
    table_name: str = Field(description="DynamoDB table name")
    service_name: str = Field(description="Powertools service name", default="rest-api")
    metrics_namespace: str = Field(description="Powertools metrics namespace", default="RestApi")
