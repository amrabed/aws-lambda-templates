from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.utilities.data_classes import S3Event
from aws_lambda_powertools.utilities.data_classes.s3_event import S3EventRecord
from aws_lambda_powertools.utilities.typing import LambdaContext

from templates.s3.models import EventSource, ProcessedMessage
from templates.s3.queue import Queue
from templates.s3.settings import Settings

settings = Settings()  # type: ignore

logger = Logger(service=settings.powertools_service_name)
tracer = Tracer(service=settings.powertools_service_name)
metrics = Metrics(namespace="S3SQSProcessor", service=settings.powertools_service_name)

queue = Queue(settings)


class Handler:
    """Processes S3 events and publishes results to SQS."""

    def __init__(self, queue: Queue) -> None:
        """Initialize the handler with an SQS queue.

        Args:
            queue: The queue used to publish processed messages.
        """
        self._queue = queue

    @tracer.capture_method
    def _build_message(self, record: S3EventRecord) -> ProcessedMessage:
        """Construct a ProcessedMessage from an S3 record.

        Args:
            record: The S3 event record to process.

        Returns:
            A ProcessedMessage instance.
        """
        return ProcessedMessage(
            bucket=record.s3.bucket.name,
            key=record.s3.get_object.key,
            event_time=record.event_time,
            source=EventSource.s3,
        )

    @tracer.capture_method
    def handle_record(self, record: S3EventRecord) -> None:
        """Handle a single S3 event record.

        Args:
            record: The S3 event record to process.
        """
        bucket = record.s3.bucket.name
        key = record.s3.get_object.key
        event_time = record.event_time

        msg = self._build_message(record)
        self._queue.publish(msg, bucket)
        logger.info("Processed record", extra={"bucket": bucket, "key": key, "event_time": event_time})


handler = Handler(queue)


@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics
def main(event: dict, context: LambdaContext) -> dict:
    """Lambda entry point for the S3-to-SQS handler.

    Args:
        event: The S3 event containing object-creation records.
        context: The Lambda execution context.

    Returns:
        A dictionary containing batchItemFailures (empty if all succeed).

    Raises:
        ValueError: If the event shape is invalid.
        Exception: If any record fails to ensure retry by the S3 event source.
    """
    if not isinstance(event, dict) or "Records" not in event or not isinstance(event["Records"], list):
        raise ValueError("Invalid S3 event shape: missing or invalid 'Records' key")

    s3_event = S3Event(event)
    success_count = 0
    errors = []

    for record in s3_event.records:
        try:
            with tracer.provider.in_subsegment("process_record"):
                handler.handle_record(record)
                success_count += 1
        except Exception as exc:
            logger.error("Failed to process record", exc_info=exc)
            metrics.add_metric(name="publish_failure", unit="Count", value=1)
            errors.append(exc)

    metrics.add_metric(name="records_processed", unit="Count", value=success_count)

    if errors:
        raise Exception(f"Batch processing failed with {len(errors)} errors. First error: {errors[0]}")

    return {"batchItemFailures": []}
