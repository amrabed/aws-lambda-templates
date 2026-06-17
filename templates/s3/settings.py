from pydantic import Field, field_validator

from templates.settings import CommonSettings


class Settings(CommonSettings, case_sensitive=False):
    queue_url: str = Field(description="SQS queue URL to publish processed messages to")
    queue_region: str = Field(default="us-east-1", description="AWS region for the SQS client")
    service_name: str = Field(default="s3-processor", description="Powertools service name")
    metrics_namespace: str = Field(default="S3Processor", description="CloudWatch Metrics namespace")
    log_level: str = Field(default="INFO", description="Log level for the Lambda Logger")

    @field_validator("queue_url")
    @classmethod
    def validate_sqs_queue_url(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("SQS_QUEUE_URL cannot be empty")
        return value
