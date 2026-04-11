from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration settings for the GraphQL Lambda function."""

    table_name: str = Field(description="The name of the DynamoDB table.")
    service_name: str = Field(description="The name of the service.", default="graphql-api")
    metrics_namespace: str = Field(description="The CloudWatch Metrics namespace.", default="GraphQLApi")
