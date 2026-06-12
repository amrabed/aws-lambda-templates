from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.event_handler.api_gateway import Response
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import ValidationError

from templates.api.models import Item
from templates.api.response import JsonResponse
from templates.api.settings import Settings
from templates.repository import Repository

settings = Settings()

logger = Logger(service=settings.service_name)
tracer = Tracer(service=settings.service_name)
metrics = Metrics(namespace=settings.metrics_namespace)

repository = Repository(settings.table_name)
app = APIGatewayRestResolver()


@app.get("/items/<id>")
def get_item(id: str) -> Response:
    """Retrieve an item by ID.

    Args:
        id: The unique identifier of the item.

    Returns:
        200 with the item, 404 if not found, or 500 on error.
    """
    try:
        if (item := repository.get_item(id)) is None:
            return JsonResponse({"message": "Not found"}, status_code=404)
        item = Item.model_validate(item)  # Validate model after retrieval to ensure data integrity
    except Exception as exc:
        message = "Item validation failed" if isinstance(exc, ValidationError) else "Error retrieving item"
        logger.error(message, exc_info=exc, extra={"item_id": id})
        return JsonResponse({"message": "Internal server error"}, status_code=500)

    return JsonResponse(item.dump())


@app.post("/items")
def create_item() -> Response:
    """Create a new item from the request body.

    Returns:
        201 with the created item, 422 on validation error, or 500 on error.
    """
    try:
        item = Item.model_validate_json(app.current_event.body)
    except ValidationError as exc:
        return JsonResponse({"errors": exc.errors()}, status_code=422)

    try:
        repository.put_item(item.model_dump())
    except Exception as exc:
        logger.error("DynamoDB put_item failed", exc_info=exc, extra={"item_id": item.id})
        return JsonResponse({"message": "Internal server error"}, status_code=500)

    return JsonResponse(item.dump(), status_code=201)


@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics
def main(event: dict, context: LambdaContext) -> dict:
    """Lambda entry point for the API Gateway handler.

    Args:
        event: The API Gateway proxy event.
        context: The Lambda execution context.

    Returns:
        The API Gateway proxy response.
    """
    return app.resolve(event, context)
