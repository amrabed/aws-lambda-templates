from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.event_handler import BedrockAgentFunctionResolver
from aws_lambda_powertools.utilities.data_classes import BedrockAgentEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import ValidationError

from templates.agent.models import Item
from templates.agent.settings import Settings
from templates.models import Entity
from templates.repository import Repository

settings = Settings()  # type: ignore

logger = Logger(service=settings.service_name)
tracer = Tracer(service=settings.service_name)
metrics = Metrics(service=settings.service_name, namespace=settings.metrics_namespace)

repository = Repository(settings.table_name)
app = BedrockAgentFunctionResolver()


@tracer.capture_method
@app.tool(name="getItem", description="Gets item details by ID")
def get_item(item_id: str) -> dict:
    """Retrieve an item by its ID.

    Args:
        item_id: The unique identifier of the item.

    Returns:
        The item details or an error message.
    """
    logger.info("Retrieving item", extra={"itemId": item_id})
    try:
        Entity(id=item_id)  # Validate ID format before querying repository
    except ValidationError:
        logger.warning("Invalid item ID provided", extra={"itemId": item_id})
        return {"error": "Invalid item ID format"}

    try:
        item = repository.get_item(item_id)
        if not item:
            return {"error": f"Item {item_id} not found"}
        return Item.model_validate(item).dump()
    except ValidationError as error:
        logger.error("Item validation failed", extra={"itemId": item_id}, exc_info=error)
        return {"error": "Internal server error"}
    except Exception as error:
        logger.error("Failed to get item", extra={"itemId": item_id}, exc_info=error)
        return {"error": f"Failed to get item with ID '{item_id}'"}


@tracer.capture_method
@app.tool(name="createItem", description="Creates a new item with name and optional description")
def create_item(item_id: str, name: str, description: str | None = None) -> dict:
    """Create a new item.

    Args:
        item_id: Unique identifier for the item.
        name: Name of the item.
        description: Optional description of the item.

    Returns:
        The created item details.
    """
    logger.info("Creating item", extra={"itemId": item_id})
    try:
        item = Item(id=item_id, name=name, description=description).dump()
        repository.put_item(item)
        return item
    except ValidationError as error:
        logger.warning("Invalid item data provided", extra={"itemId": item_id}, exc_info=error)
        return {"error": "Invalid item data"}
    except Exception as error:
        logger.error("Failed to create item", extra={"itemId": item_id}, exc_info=error)
        return {"error": f"Failed to create item with ID '{item_id}'"}


@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics
def main(event: dict | BedrockAgentEvent, context: LambdaContext) -> dict:
    """Lambda entry point for the Bedrock Agent handler.

    Args:
        event: The Bedrock Agent event.
        context: The Lambda execution context.

    Returns:
        The Bedrock Agent function response.
    """
    return app.resolve(event, context)
