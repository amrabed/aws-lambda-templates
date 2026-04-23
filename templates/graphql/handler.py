from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.event_handler import AppSyncResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.parameters import DynamoDBProvider
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import ValidationError

from templates.graphql.models import Item
from templates.graphql.settings import Settings

settings = Settings()  # type: ignore

logger = Logger(service=settings.service_name)
tracer = Tracer(service=settings.service_name)
metrics = Metrics(namespace=settings.metrics_namespace)

provider = DynamoDBProvider(settings.table_name)
app = AppSyncResolver()


@app.resolver(type_name="Query", field_name="getItem")
@tracer.capture_method
def get_item(id: str) -> dict | None:
    """Retrieve an item by ID.

    Args:
        id: The unique identifier of the item.

    Returns:
        The item if found, or None.
    """
    try:
        return provider.table.get_item(Key={"id": id}).get("Item")
    except Exception as error:
        raise RuntimeError(f"Failed to get item with ID '{id}'. Cause: {error}") from error


@app.resolver(type_name="Query", field_name="listItems")
@tracer.capture_method
def list_items() -> list[dict]:
    """Retrieve all items.

    Returns:
        A list of items.
    """
    try:
        return provider.table.scan().get("Items", [])
    except Exception as error:
        raise RuntimeError(f"Failed to list items. Cause: {error}") from error


@app.resolver(type_name="Mutation", field_name="createItem")
@tracer.capture_method
def create_item(name: str) -> dict:
    """Create a new item.

    Args:
        name: The name of the item.

    Returns:
        The created item.
    """
    try:
        item = Item(name=name).dump()
        provider.table.put_item(Item=item)
        return item
    except (ValidationError, Exception) as error:
        raise RuntimeError(f"Failed to create item with name '{name}'. Cause: {error}") from error


@logger.inject_lambda_context(correlation_id_path=correlation_paths.APPSYNC_RESOLVER)
@tracer.capture_lambda_handler
@metrics.log_metrics
def main(event: dict, context: LambdaContext) -> dict:
    """Lambda entry point for the AppSync resolver.

    Args:
        event: The AppSync resolver event.
        context: The Lambda execution context.

    Returns:
        The resolved data.
    """
    return app.resolve(event, context)
