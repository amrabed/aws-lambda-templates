from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel


class SourceItem(BaseModel, populate_by_name=True, alias_generator=to_camel, from_attributes=True):
    id: str = Field(description="Unique item identifier", min_length=1, max_length=50)
    name: str | None = Field(default=None, description="Human-readable item name", min_length=1, max_length=100)


class DestinationItem(BaseModel, populate_by_name=True, alias_generator=to_camel, from_attributes=True):
    id: str = Field(description="Unique item identifier", min_length=1, max_length=50)
    name: str | None = Field(default=None, description="Human-readable item name", min_length=1, max_length=100)
