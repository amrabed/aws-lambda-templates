from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel


class SourceItem(BaseModel, populate_by_name=True, alias_generator=to_camel):
    id: str = Field(description="Unique item identifier")
    name: str | None = Field(default=None, description="Human-readable item name")


class DestinationItem(BaseModel, populate_by_name=True, alias_generator=to_camel):
    id: str = Field(description="Unique item identifier")
    name: str | None = Field(default=None, description="Human-readable item name")
