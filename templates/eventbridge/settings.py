from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings, case_sensitive=False):
    api_url: str = Field(description="URL of the external HTTP API to call")
    api_timeout_seconds: int = Field(description="Timeout for the external API call in seconds", default=10)
    api_max_retries: int = Field(description="Maximum number of retries for the external API call", default=3)
    api_backoff_factor: float = Field(description="Backoff factor for API retries", default=0.3)

    secret_name: str = Field(description="AWS Secrets Manager secret name holding the API token")
    secret_cache_max_age: int = Field(description="Maximum age of the cached secret in seconds", default=60)
    secret_manager_max_retries: int = Field(
        description="Maximum number of retry attempts for AWS service calls", default=3
    )

    table_name: str = Field(description="DynamoDB table name for persisting API responses")
    service_name: str = Field(description="Powertools service name used for Logger and Tracer")
    metrics_namespace: str = Field(description="CloudWatch namespace for Powertools Metrics")
