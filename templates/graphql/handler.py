from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.event_handler import AppSyncResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import ValidationError

from templates.graphql.models import Item
from templates.graphql.settings import Settings
from templates.models import Entity
from templates.repository import Repository

settings = Settings()  # type: ignore

logger = Logger(service=settings.service_name)
tracer = Tracer(service=settings.service_name)
metrics = Metrics(namespace=settings.metrics_namespace)

repository = Repository(settings.table_name)
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
        Entity(id=id)
    except ValidationError:
        logger.warning("Invalid item ID provided", extra={"itemId": id})
        raise RuntimeError(f"Invalid item ID '{id}'") from None

    try:
        if (item := repository.get_item(id)) is None:
            return None
        return Item.model_validate(item).dump()
    except Exception as error:
        is_val_error = isinstance(error, ValidationError)
        message = "Item validation failed" if is_val_error else f"Failed to get item with ID '{id}'"
        logger.error(message, extra={"itemId": id}, exc_info=error)
        raise RuntimeError(message) from None


@app.resolver(type_name="Query", field_name="listItems")
@tracer.capture_method
def list_items() -> list[dict]:
    """Retrieve all items.

    Returns:
        A list of items.
    """
    try:
        return [Item.model_validate(item).dump() for item in repository.list_items()]
    except Exception as error:
        logger.error("Failed to list items", exc_info=error)
        raise RuntimeError("Failed to list items") from None


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
        repository.put_item(item)
        return item
    except ValidationError as error:
        logger.warning("Invalid item data provided", extra={"itemName": name}, exc_info=error)
        raise RuntimeError("Invalid item data") from None
    except Exception as error:
        logger.error("Failed to create item", extra={"itemName": name}, exc_info=error)
        raise RuntimeError(f"Failed to create item with name '{name}'") from None


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
