from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class CommonSettings(BaseSettings):
    """Common settings shared by all Lambda functions."""

    model_config = ConfigDict(case_sensitive=False)

    service_name: str = Field(description="Powertools service name")
    metrics_namespace: str = Field(description="Powertools metrics namespace")
    log_level: str = Field(description="Logging level", default="INFO")
