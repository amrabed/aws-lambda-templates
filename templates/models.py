from typing import Any

from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class BaseTemplateModel(BaseModel, populate_by_name=True, alias_generator=to_camel):
    """Base model for all template data models with common configuration and helper methods."""

    def dump(self, **kwargs: Any) -> dict[str, Any]:
        """Dump the model to a dictionary with default settings (camelCase, exclude None)."""
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        return self.model_dump(**kwargs)

    def dump_json(self, **kwargs: Any) -> str:
        """Dump the model to a JSON string with default settings (camelCase, exclude None)."""
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        return self.model_dump_json(**kwargs)
