from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel


class Item(BaseModel, populate_by_name=True, alias_generator=to_camel):
    id: str = Field(description="Unique item identifier.")
    name: str = Field(description="Human-readable item name.")
