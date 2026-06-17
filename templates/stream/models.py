from pydantic import Field

from templates.models import BaseTemplateModel


class SourceItem(BaseTemplateModel, from_attributes=True):
    id: str = Field(description="Unique item identifier", min_length=1, max_length=50)
    name: str | None = Field(default=None, description="Human-readable item name", min_length=1, max_length=100)


class DestinationItem(BaseTemplateModel, from_attributes=True):
    id: str = Field(description="Unique item identifier", min_length=1, max_length=50)
    name: str | None = Field(default=None, description="Human-readable item name", min_length=1, max_length=100)
