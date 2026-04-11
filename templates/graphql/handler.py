from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.event_handler import AppSyncResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import ValidationError

from templates.graphql.models import Item
from templates.graphql.settings import Settings
from templates.repository import Repository

settings = Settings()

logger = Logger(service=settings.service_name)
tracer = Tracer(service=settings.service_name)
metrics = Metrics(namespace=settings.metrics_namespace)

repository = Repository(settings.table_name)
app = AppSyncResolver()


def get_repository() -> Repository:
    return repository


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
        return get_repository().get_item(id)
    except Exception as exc:
        logger.error("DynamoDB get_item failed", exc_info=exc)
        raise


@app.resolver(type_name="Query", field_name="listItems")
@tracer.capture_method
def list_items() -> list[dict]:
    """Retrieve all items.

    Returns:
        A list of items.
    """
    try:
        return get_repository().list_items()
    except Exception as exc:
        logger.error("DynamoDB list_items failed", exc_info=exc)
        raise


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
        item = Item(name=name)
        get_repository().put_item(item.model_dump())
        return item.dump()
    except (ValidationError, Exception) as exc:
        logger.error("Failed to create item", exc_info=exc)
        raise


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
