from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.batch import BatchProcessor, EventType, process_partial_response
from aws_lambda_powertools.utilities.data_classes.dynamo_db_stream_event import DynamoDBRecord
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3.dynamodb.types import TypeDeserializer
from pydantic import ValidationError

from templates.repository import Repository
from templates.stream.models import DestinationItem, SourceItem
from templates.stream.settings import Settings

settings = Settings()
logger = Logger(service=settings.service_name)
tracer = Tracer(service=settings.service_name)
metrics = Metrics(namespace=settings.metrics_namespace)

repository = Repository(settings.destination_table_name)
processor = BatchProcessor(event_type=EventType.DynamoDBStreams)


class Handler:
    def __init__(self, repository: Repository) -> None:
        self._repository = repository

    @tracer.capture_method
    def _process(self, item: SourceItem) -> DestinationItem | None:
        """Process received item into a DestinationItem"""
        try:
            # TODO: process here
            return DestinationItem.model_validate(item.model_dump(by_alias=True))
        except ValidationError as exc:
            logger.error("DestinationItem validation failed", exc_info=exc)
            return None

    @tracer.capture_method
    def handle_record(self, record: DynamoDBRecord) -> None:
        event_name = record.event_name

        if event_name and event_name.name in ("INSERT", "MODIFY"):
            item = self._process(SourceItem.model_validate(record.dynamodb.new_image))
            if item is None:
                raise ValueError("Failed to process record into DestinationItem")
            self._repository.put_item(item.model_dump())
        elif event_name and event_name.name == "REMOVE":
            plain_keys = SourceItem.model_validate(record.dynamodb.keys)
            self._repository.delete_item(plain_keys.model_dump(exclude_none=True))


handler = Handler(repository)


@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics
def main(event: dict, context: LambdaContext) -> dict:
    return process_partial_response(
        event=event,
        record_handler=handler.handle_record,
        processor=processor,
        context=context,
    )
