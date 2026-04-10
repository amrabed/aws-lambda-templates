from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.utilities.data_classes import S3Event
from aws_lambda_powertools.utilities.data_classes.s3_event import S3EventRecord
from aws_lambda_powertools.utilities.typing import LambdaContext

from templates.queue import Queue
from templates.s3.models import ProcessedMessage
from templates.s3.settings import Settings

settings = Settings()  # type: ignore

logger = Logger(service=settings.service_name)
tracer = Tracer(service=settings.service_name)
metrics = Metrics(namespace=settings.metrics_namespace, service=settings.service_name)

queue = Queue(settings.queue_url, settings.queue_region)


@tracer.capture_method
def handle_record(record: S3EventRecord) -> None:
    """Handle a single S3 event record.

    Args:
        record: The S3 event record to process.
    """
    message = {"bucket": record.s3.bucket.name, "key": record.s3.get_object.key, "event_time": record.event_time}
    queue.publish(ProcessedMessage.model_validate(message).model_dump_json(by_alias=True, exclude_none=True))
    logger.info("Processed record", extra=message)


@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics
def main(event: S3Event, context: LambdaContext) -> dict:
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
    processed = 0
    errors = []
    for record in event.records:
        try:
            handle_record(record)
            processed += 1
        except Exception as error:
            logger.error("Failed to process record", exc_info=error)
            metrics.add_metric(name="publish_failure", unit="Count", value=1)
            errors.append(error)

    metrics.add_metric(name="records_processed", unit="Count", value=processed)

    if errors:
        raise Exception(f"Batch processing failed with {len(errors)} errors. First error: {errors[0]}")

    return {"batchItemFailures": []}
