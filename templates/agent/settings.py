from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings, case_sensitive=False):
    """Configuration settings for the Bedrock Agent Lambda function."""

    table_name: str = Field(description="Name of the DynamoDB table to store agent items.")
    service_name: str = Field(description="Name of the service for logging and tracing.", default="bedrock-agent")
    metrics_namespace: str = Field(description="Namespace for custom CloudWatch metrics.", default="BedrockAgent")
