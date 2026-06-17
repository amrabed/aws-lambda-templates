from pydantic import Field

from templates.settings import CommonSettings


class Settings(CommonSettings, case_sensitive=False):
    """Configuration settings for the SQS Lambda function."""

    table_name: str = Field(description="Name of the DynamoDB table to store processed items.")
    service_name: str = "sqs-processor"
    metrics_namespace: str = "SqsProcessor"
