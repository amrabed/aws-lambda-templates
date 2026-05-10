from typing import Any

from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel


class Item(BaseModel, populate_by_name=True, alias_generator=to_camel):
    """Model representing an item managed by the agent."""

    id: str = Field(description="Unique identifier for the item.")
    name: str = Field(description="Name of the item.")
    description: str | None = Field(description="Description of the item.", default=None)

    def dump(self, **kwargs: Any) -> dict:
        """Dump the model to a dictionary with default settings for responses."""
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        return self.model_dump(**kwargs)
