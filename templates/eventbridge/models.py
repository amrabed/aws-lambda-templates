from typing import Any

from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel


class ApiResponse(BaseModel, populate_by_name=True, alias_generator=to_camel):
    id: str = Field(description="Unique identifier of the API response record", min_length=1, max_length=50)
    message: str = Field(description="Message returned by the external API", min_length=1, max_length=1000)

    def dump(self, **kwargs: Any) -> dict:
        """Dump the model to a dictionary with default settings for responses."""
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        return self.model_dump(**kwargs)
