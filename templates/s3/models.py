from enum import StrEnum

from pydantic import Field

from templates.models import Object


class EventSource(StrEnum):
    s3 = "s3"


class ProcessedMessage(Object):
    bucket: str = Field(description="S3 bucket name", min_length=3, max_length=63)
    key: str = Field(description="S3 object key", min_length=1, max_length=1024)
    event_time: str = Field(description="ISO-8601 event timestamp")
    source: EventSource = Field(default=EventSource.s3, description="Origin event source")
