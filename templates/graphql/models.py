from uuid import uuid4

from pydantic import Field

from templates.models import BaseTemplateModel


class Item(BaseTemplateModel):
    id: str = Field(
        description="Unique item identifier", default_factory=lambda: str(uuid4()), min_length=1, max_length=50
    )
    name: str = Field(description="Human-readable item name", min_length=1, max_length=100)
