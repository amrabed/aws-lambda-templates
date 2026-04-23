from json import dumps, loads

from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.event_handler.api_gateway import Response
from aws_lambda_powertools.utilities.parameters import DynamoDBProvider
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import ValidationError

from templates.api.models import Item
from templates.api.settings import Settings

settings = Settings()

logger = Logger(service=settings.service_name)
tracer = Tracer(service=settings.service_name)
metrics = Metrics(namespace=settings.metrics_namespace)

provider = DynamoDBProvider(settings.table_name)
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
        item = provider.table.get_item(Key={"id": id}).get("Item")
    except Exception as exc:
        logger.error("DynamoDB get_item failed", exc_info=exc)
        return Response(
            status_code=500, content_type="application/json", body=dumps({"message": "Internal server error"})
        )

    if item is None:
        return Response(status_code=404, content_type="application/json", body=dumps({"message": "Not found"}))

    return Response(status_code=200, content_type="application/json", body=dumps(item))


@app.post("/items")
def create_item() -> Response:
    """Create a new item from the request body.

    Returns:
        201 with the created item, 422 on validation error, or 500 on error.
    """
    body = app.current_event.json_body

    try:
        item = Item.model_validate(body)
    except ValidationError as exc:
        return Response(status_code=422, content_type="application/json", body=dumps({"errors": loads(exc.json())}))

    try:
        provider.table.put_item(Item=item.model_dump())
    except Exception as exc:
        logger.error("DynamoDB put_item failed", exc_info=exc)
        return Response(
            status_code=500, content_type="application/json", body=dumps({"message": "Internal server error"})
        )

    return Response(status_code=201, content_type="application/json", body=dumps(item.dump()))


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
