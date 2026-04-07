from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    table_name: str = Field(description="DynamoDB table name")
    service_name: str = Field(description="Powertools service name")
    metrics_namespace: str = Field(description="Powertools metrics namespace")
