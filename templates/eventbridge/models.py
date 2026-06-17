from pydantic import Field

from templates.models import BaseTemplateModel


class ApiResponse(BaseTemplateModel):
    id: str = Field(description="Unique identifier of the API response record", min_length=1, max_length=50)
    message: str = Field(description="Message returned by the external API", min_length=1, max_length=1000)
