from pydantic import Field
from pydantic_settings import BaseSettings


class CommonSettings(BaseSettings):
    """Common configuration settings shared by all Lambda functions."""

    service_name: str = Field(description="Powertools service name")
    metrics_namespace: str = Field(description="Powertools metrics namespace")
    log_level: str = Field(description="Logging level", default="INFO")
