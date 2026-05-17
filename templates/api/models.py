from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel


class Item(BaseModel, populate_by_name=True, alias_generator=to_camel):
    id: str = Field(
        description="Unique item identifier", default_factory=lambda: str(uuid4()), min_length=1, max_length=50
    )
    name: str = Field(description="Human-readable item name", min_length=1, max_length=100)

    def dump(self, **kwargs: Any) -> str:
        """Dump the model to a JSON string with default settings for API responses."""
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        return self.model_dump_json(**kwargs)
