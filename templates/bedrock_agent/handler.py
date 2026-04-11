from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.event_handler import BedrockAgentFunctionResolver
from aws_lambda_powertools.utilities.data_classes import BedrockAgentEvent
from aws_lambda_powertools.utilities.typing import LambdaContext

from templates.bedrock_agent.models import Item
from templates.bedrock_agent.settings import Settings
from templates.repository import Repository

settings = Settings()  # type: ignore

logger = Logger(service=settings.service_name)
tracer = Tracer(service=settings.service_name)
metrics = Metrics(service=settings.service_name, namespace=settings.metrics_namespace)

repository = Repository(settings.table_name)
app = BedrockAgentFunctionResolver()


@tracer.capture_method
def get_item_logic(item_id: str) -> dict:
    """Retrieve an item by its ID.

    Args:
        item_id: The unique identifier of the item.

    Returns:
        The item details or an error message.
    """
    logger.info(f"Retrieving item {item_id}")
    item = repository.get_item(item_id)
    if not item:
        return {"error": f"Item {item_id} not found"}
    return item


@tracer.capture_method
def create_item_logic(item_id: str, name: str, description: str | None = None) -> dict:
    """Create a new item.

    Args:
        item_id: Unique identifier for the item.
        name: Name of the item.
        description: Optional description of the item.

    Returns:
        The created item details.
    """
    logger.info(f"Creating item {item_id}")
    item = Item(id=item_id, name=name, description=description)
    repository.put_item(item.model_dump())
    return item.model_dump(by_alias=True, exclude_none=True)


@app.tool(name="getItem", description="Gets item details by ID")
def get_item(item_id: str) -> dict:
    """Tool to retrieve an item."""
    return get_item_logic(item_id)


@app.tool(name="createItem", description="Creates a new item with name and optional description")
def create_item(item_id: str, name: str, description: str | None = None) -> dict:
    """Tool to create an item."""
    return create_item_logic(item_id, name, description)


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
