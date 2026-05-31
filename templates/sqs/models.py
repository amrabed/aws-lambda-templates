from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel


class SqsMessage(BaseModel, populate_by_name=True, alias_generator=to_camel):
    """Model representing the expected SQS message body."""

    id: str = Field(description="Unique identifier for the message.", min_length=1, max_length=50)
    content: str = Field(description="The main content of the message.", min_length=1, max_length=1000)


class ProcessedItem(BaseModel, populate_by_name=True, alias_generator=to_camel):
    """Model representing the item to be stored in DynamoDB."""

    id: str = Field(description="Unique identifier for the item (partition key).", min_length=1, max_length=50)
    content: str = Field(description="The processed content.", min_length=1, max_length=1000)
    status: str = Field(description="Processing status.", min_length=1, max_length=50)
