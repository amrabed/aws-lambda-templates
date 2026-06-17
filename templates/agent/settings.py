from pydantic import Field

from templates.settings import CommonSettings


class Settings(CommonSettings):
    """Configuration settings for the Bedrock Agent Lambda function."""

    table_name: str = Field(description="Name of the DynamoDB table to store agent items.")
    service_name: str = "bedrock-agent"
    metrics_namespace: str = "BedrockAgent"
