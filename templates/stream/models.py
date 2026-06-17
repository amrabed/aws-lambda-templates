from pydantic import Field

from templates.models import Entity


class SourceItem(Entity, from_attributes=True):
    name: str | None = Field(default=None, description="Human-readable item name", min_length=1, max_length=100)


class DestinationItem(Entity, from_attributes=True):
    name: str | None = Field(default=None, description="Human-readable item name", min_length=1, max_length=100)
