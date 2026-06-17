from pydantic import Field

from templates.models import BaseTemplateModel


class Item(BaseTemplateModel):
    """Model representing an item managed by the agent."""

    id: str = Field(description="Unique identifier for the item.", min_length=1, max_length=50)
    name: str = Field(description="Name of the item.", min_length=1, max_length=100)
    description: str | None = Field(description="Description of the item.", default=None, max_length=500)
