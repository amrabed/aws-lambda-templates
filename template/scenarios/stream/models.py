from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel


class DestinationItem(BaseModel, extra="allow", populate_by_name=True, alias_generator=to_camel):
    id: str = Field(description="Unique item identifier.")
