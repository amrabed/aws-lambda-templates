from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings, case_sensitive=False):
    sqs_queue_url: str = Field(description="SQS queue URL to publish processed messages to")
    aws_region: str = Field(default="us-east-1", description="AWS region for the SQS client")
    powertools_service_name: str = Field(default="s3-sqs-processor", description="Powertools service name")
    log_level: str = Field(default="INFO", description="Log level for the Lambda Logger")

    @field_validator("sqs_queue_url")
    @classmethod
    def validate_sqs_queue_url(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("SQS_QUEUE_URL cannot be empty")
        return v


def get_settings() -> Settings:
    return Settings()  # type: ignore
