from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings, case_sensitive=False):
    api_url: str = Field(description="URL of the external HTTP API to call")
    api_timeout_seconds: int = Field(description="Timeout for the external API call in seconds", default=10)
    secret_name: str = Field(description="AWS Secrets Manager secret name holding the API token")
    table_name: str = Field(description="DynamoDB table name for persisting API responses")
    service_name: str = Field(description="Powertools service name used for Logger and Tracer")
    metrics_namespace: str = Field(description="CloudWatch namespace for Powertools Metrics")
