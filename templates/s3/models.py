from enum import StrEnum

from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel


class EventSource(StrEnum):
    s3 = "s3"


class ProcessedMessage(BaseModel, populate_by_name=True, alias_generator=to_camel):
    bucket: str = Field(description="S3 bucket name")
    key: str = Field(description="S3 object key")
    event_time: str = Field(description="ISO-8601 event timestamp")
    source: EventSource = Field(default=EventSource.s3, description="Origin event source")
