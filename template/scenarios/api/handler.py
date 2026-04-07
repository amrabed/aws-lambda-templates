from __future__ import annotations

import json

import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.event_handler.exceptions import NotFoundError
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import ValidationError

from template.scenarios.api.models import Item
from template.scenarios.api.repository import Repository
from template.scenarios.api.settings import Settings

settings = Settings()
logger = Logger(service=settings.service_name)
tracer = Tracer(service=settings.service_name)
metrics = Metrics(namespace=settings.metrics_namespace)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(settings.table_name)


class Handler:
    def __init__(self, repository: Repository) -> None:
        self._repo = repository
        self._app = APIGatewayRestResolver()
        self._register_routes()

    def _register_routes(self) -> None:
        self._app.get("/items/<id>")(self._get_item)
        self._app.post("/items")(self._create_item)

    def handle(self, event: dict, context: LambdaContext) -> dict:
        return self._app.resolve(event, context)  # type: ignore[return-value]

    def _get_item(self, id: str) -> dict:  # noqa: A002
        try:
            item = self._repo.get_item(id)
        except Exception as exc:
            logger.error("DynamoDB get_item failed", exc_info=exc)
            return self._app.current_event.json_body, 500  # type: ignore[return-value]

        if item is None:
            raise NotFoundError(f"Item '{id}' not found")

        return item  # type: ignore[return-value]

    def _create_item(self) -> tuple[dict, int]:
        body = self._app.current_event.json_body

        try:
            item = Item.model_validate(body)
        except ValidationError as exc:
            return {"errors": json.loads(exc.json())}, 422

        try:
            self._repo.put_item(item.model_dump())
        except Exception as exc:
            logger.error("DynamoDB put_item failed", exc_info=exc)
            return {"message": "Internal server error"}, 500

        return item.model_dump(), 201


@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics
def main(event: dict, context: LambdaContext) -> dict:
    repo = Repository(table)
    return Handler(repo).handle(event, context)
