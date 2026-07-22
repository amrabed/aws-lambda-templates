from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.batch import BatchProcessor, EventType, process_partial_response
from aws_lambda_powertools.utilities.data_classes.dynamo_db_stream_event import DynamoDBRecord
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import ValidationError

from templates.repository import Repository
from templates.stream.models import DestinationItem
from templates.stream.settings import Settings

settings = Settings()
logger = Logger(service=settings.service_name)
tracer = Tracer(service=settings.service_name)
metrics = Metrics(namespace=settings.metrics_namespace)

repository = Repository(settings.destination_table_name)
processor = BatchProcessor(event_type=EventType.DynamoDBStreams)


class Handler:
    """Processes DynamoDB Stream records and writes results to a destination table."""

    def __init__(self, repository: Repository) -> None:
        """Initialize the handler with a destination repository.

        Args:
            repository: The repository used to write processed items.
        """
        self._repository = repository

    @tracer.capture_method
    def _process(self, item: dict) -> DestinationItem | None:
        """Transform a source item dictionary into a destination item.

        Args:
            item: The source item dictionary to process.

        Returns:
            A `DestinationItem` on success, or `None` if validation fails.
        """
        try:
            # Optimize: Bypass redundant SourceItem validation by validating the record dictionary
            # directly against DestinationItem, avoiding double model validation overhead.
            return DestinationItem.model_validate(item)
        except ValidationError as exc:
            logger.error("DestinationItem validation failed", exc_info=exc)
            return None

    @tracer.capture_method
    def handle_record(self, record: DynamoDBRecord) -> None:
        """Handle a single DynamoDB Stream record.

        Processes INSERT and MODIFY events by transforming and writing the new image
        to the destination table. Handles REMOVE events by deleting the corresponding
        item from the destination table.

        Args:
            record: The DynamoDB Stream record to process.

        Raises:
            ValueError: If the record cannot be transformed into a `DestinationItem` or is invalid.
        """
        event_name = record.event_name

        # Ensure record.dynamodb is not None before accessing new_image or keys to prevent runtime errors
        if not record.dynamodb:
            logger.error("Record dynamodb property is None", extra={"record": record})
            raise ValueError("Invalid record: missing dynamodb data")

        if event_name and event_name.name in ("INSERT", "MODIFY"):
            if record.dynamodb.new_image is None:
                raise ValueError("Failed to process record: new_image is None")
            item = self._process(record.dynamodb.new_image)
            if item is None:
                raise ValueError("Failed to process record into DestinationItem")
            # Optimize: Use .dump() helper method for consistent camelCase and null field exclusion
            self._repository.put_item(item.dump())
        elif event_name and event_name.name == "REMOVE":
            if record.dynamodb.keys is None:
                raise ValueError("Failed to process REMOVE record: keys is None")
            item_id = record.dynamodb.keys.get("id")
            if not item_id:
                raise ValueError("Failed to process REMOVE record: 'id' is missing in keys")
            # Optimize: Bypass SourceItem validation for REMOVE events by passing the key string directly
            self._repository.delete_item(str(item_id))


handler = Handler(repository)


@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics
def main(event: dict, context: LambdaContext) -> dict:
    """Lambda entry point for the DynamoDB Streams handler.

    Args:
        event: The DynamoDB Streams event containing a batch of records.
        context: The Lambda execution context.

    Returns:
        A partial batch response indicating which records failed processing.
    """
    return process_partial_response(
        event=event,
        record_handler=handler.handle_record,
        processor=processor,
        context=context,
    )
