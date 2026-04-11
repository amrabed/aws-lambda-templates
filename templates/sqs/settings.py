from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings, case_sensitive=False):
    """Configuration settings for the SQS Lambda function."""

    table_name: str = Field(description="Name of the DynamoDB table to store processed items.")
    service_name: str = Field(description="Name of the service for logging and tracing.", default="sqs-processor")
    metrics_namespace: str = Field(description="Namespace for custom CloudWatch metrics.", default="SqsProcessor")
