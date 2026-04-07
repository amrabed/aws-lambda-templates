from __future__ import annotations

import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.data_classes import DynamoDBStreamEvent, event_source
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3.dynamodb.types import TypeDeserializer
from pydantic import ValidationError

from template.scenarios.stream.models import DestinationItem
from template.scenarios.stream.repository import Repository
from template.scenarios.stream.settings import Settings

settings = Settings()
logger = Logger(service=settings.service_name)
tracer = Tracer(service=settings.service_name)
metrics = Metrics(namespace=settings.metrics_namespace)

dynamodb = boto3.resource("dynamodb")
destination_table = dynamodb.Table(settings.destination_table_name)

_deserializer = TypeDeserializer()


def _deserialize_image(image: dict) -> dict:
    return {k: _deserializer.deserialize(v) for k, v in image.items()}


class Handler:
    def __init__(self, repository: Repository) -> None:
        self._repo = repository

    def handle(self, event: DynamoDBStreamEvent, context: LambdaContext) -> None:
        for record in event.records:
            try:
                event_name = record.event_name

                if event_name.name in ("INSERT", "MODIFY"):
                    plain = dict(record.dynamodb.new_image)  # type: ignore[union-attr]
                    item = DestinationItem.model_validate(plain)
                    self._repo.put_item(item.model_dump())

                elif event_name.name == "REMOVE":
                    key = dict(record.dynamodb.keys)  # type: ignore[union-attr]
                    self._repo.delete_item(key)

            except (ValidationError, Exception) as exc:
                logger.error("Failed to process record", exc_info=exc, extra={"record": record.raw_event})
                metrics.add_metric(name="ProcessingError", unit=MetricUnit.Count, value=1)
                continue


@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics
@event_source(data_class=DynamoDBStreamEvent)
def main(event: DynamoDBStreamEvent, context: LambdaContext) -> None:
    repo = Repository(destination_table)
    Handler(repo).handle(event, context)
