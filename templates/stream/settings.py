from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings, case_sensitive=False):
    destination_table_name: str = Field(description="Destination DynamoDB table name")
    service_name: str = Field(description="Powertools service name")
    metrics_namespace: str = Field(description="Powertools metrics namespace")
