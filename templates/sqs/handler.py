from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.utilities.batch import BatchProcessor, EventType, process_partial_response
from aws_lambda_powertools.utilities.batch.types import PartialItemFailureResponse
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities.typing import LambdaContext

from templates.repository import Repository
from templates.sqs.models import ProcessedItem, SqsMessage
from templates.sqs.settings import Settings

settings = Settings()  # type: ignore


logger = Logger(service=settings.service_name)
tracer = Tracer(service=settings.service_name)
metrics = Metrics(service=settings.service_name, namespace=settings.metrics_namespace)

repository = Repository(settings.table_name)
processor = BatchProcessor(event_type=EventType.SQS)


class Handler:
    """Processes SQS messages and stores results in a DynamoDB table."""

    def __init__(self, repository: Repository) -> None:
        """Initialize the handler with a repository.

        Args:
            repository: The repository used to store processed items.
        """
        self._repository = repository

    @tracer.capture_method
    def handle_record(self, record: SQSRecord) -> None:
        """Handle a single SQS record.

        Args:
            record: The SQS record to process.

        Raises:
            ValueError: If the message body cannot be parsed or processed.
        """
        try:
            message = SqsMessage.model_validate_json(record.body)
            processed = ProcessedItem(id=message.id, content=message.content, status="PROCESSED")
            self._repository.put_item(processed.model_dump())
            logger.info("Successfully processed and stored message", extra={"messageId": message.id})
        except Exception as exc:
            logger.error("Failed to process SQS record", exc_info=exc)
            raise


handler = Handler(repository)


@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics
def main(event: dict, context: LambdaContext) -> PartialItemFailureResponse:
    """Lambda entry point for the SQS-to-DynamoDB handler.

    Args:
        event: The SQS event containing a batch of messages.
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
