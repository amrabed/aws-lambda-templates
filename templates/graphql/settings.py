from pydantic import Field

from templates.settings import CommonSettings


class Settings(CommonSettings):
    """Configuration settings for the GraphQL Lambda function."""

    table_name: str = Field(description="The name of the DynamoDB table.")
    service_name: str = "graphql-api"
    metrics_namespace: str = "GraphQLApi"
