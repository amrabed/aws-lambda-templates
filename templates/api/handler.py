from json import dumps, loads

from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.event_handler.api_gateway import Response
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import ValidationError

from templates.api.models import Item
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
        item_dict = repository.get_item(id)
    except Exception as exc:
        logger.error("DynamoDB get_item failed", exc_info=exc)
        return Response(
            status_code=500, content_type="application/json", body=dumps({"message": "Internal server error"})
        )

    if item_dict is None:
        return Response(status_code=404, content_type="application/json", body=dumps({"message": "Not found"}))

    try:
        item = Item.model_validate(item_dict)
    except ValidationError as exc:
        logger.error("Item validation failed", exc_info=exc)
        return Response(
            status_code=500, content_type="application/json", body=dumps({"message": "Internal server error"})
        )

    return Response(
        status_code=200, content_type="application/json", body=dumps(item.model_dump(by_alias=True, exclude_none=True))
    )


@app.post("/items")
def create_item() -> Response:
    """Create a new item from the request body.

    Returns:
        201 with the created item, 422 on validation error, or 500 on error.
    """
    try:
        item = Item.model_validate_json(app.current_event.body)
    except ValidationError as exc:
        return Response(status_code=422, content_type="application/json", body=dumps({"errors": loads(exc.json())}))

    try:
        repository.put_item(item.model_dump())
    except Exception as exc:
        logger.error("DynamoDB put_item failed", exc_info=exc)
        return Response(
            status_code=500, content_type="application/json", body=dumps({"message": "Internal server error"})
        )

    return Response(status_code=201, content_type="application/json", body=item.dump_json())


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
