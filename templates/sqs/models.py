from pydantic import Field

from templates.models import Entity


class SqsMessage(Entity):
    """Model representing the expected SQS message body."""

    content: str = Field(description="The main content of the message.", min_length=1, max_length=1000)


class ProcessedItem(Entity):
    """Model representing the item to be stored in DynamoDB."""

    content: str = Field(description="The processed content.", min_length=1, max_length=1000)
    status: str = Field(description="Processing status.", min_length=1, max_length=50)
