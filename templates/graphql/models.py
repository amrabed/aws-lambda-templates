from pydantic import Field

from templates.models import Entity


class Item(Entity):
    name: str = Field(description="Human-readable item name", min_length=1, max_length=100)
