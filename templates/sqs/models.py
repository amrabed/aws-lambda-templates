from pydantic import Field

from templates.models import BaseTemplateModel


class SqsMessage(BaseTemplateModel):
    """Model representing the expected SQS message body."""

    id: str = Field(description="Unique identifier for the message.", min_length=1, max_length=50)
    content: str = Field(description="The main content of the message.", min_length=1, max_length=1000)


class ProcessedItem(BaseTemplateModel):
    """Model representing the item to be stored in DynamoDB."""

    id: str = Field(description="Unique identifier for the item (partition key).", min_length=1, max_length=50)
    content: str = Field(description="The processed content.", min_length=1, max_length=1000)
    status: str = Field(description="Processing status.", min_length=1, max_length=50)
