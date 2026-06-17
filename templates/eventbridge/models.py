"""Data models for the EventBridge template."""

from pydantic import Field

from templates.models import Entity


class ApiResponse(Entity):
    """Represents the response from the external API."""

    message: str = Field(description="Message returned by the external API", min_length=1, max_length=1000)
