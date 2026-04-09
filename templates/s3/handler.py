from enum import StrEnum

import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.utilities.data_classes import S3Event
from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel

from templates.s3.settings import get_settings

logger = Logger(service="s3-sqs-processor")
tracer = Tracer()
metrics = Metrics(namespace="S3SQSProcessor", service="s3-sqs-processor")
sqs_client = boto3.client("sqs", region_name="us-east-1")


class EventSource(StrEnum):
    s3 = "s3"


class ProcessedMessage(BaseModel, populate_by_name=True, alias_generator=to_camel):
    bucket: str = Field(description="S3 bucket name")
    key: str = Field(description="S3 object key")
    event_time: str = Field(description="ISO-8601 event timestamp")
    source: EventSource = Field(description="Origin event source")


def _parse_event(event: dict) -> S3Event:
    if not isinstance(event, dict) or "Records" not in event or not isinstance(event["Records"], list):
        raise ValueError("Invalid S3 event shape: missing or invalid 'Records' key")
    try:
        return S3Event(data=event)
    except Exception as e:
        logger.error(f"Failed to parse S3 event: {e}")
        raise ValueError(f"Invalid S3 event shape: {e}")


def _build_message(record) -> ProcessedMessage:
    return ProcessedMessage(
        bucket=record.s3.bucket.name,
        key=record.s3.get_object.key,
        event_time=record.event_time,
        source=EventSource.s3,
    )


def _publish(msg: ProcessedMessage, bucket: str) -> None:
    # Always reload settings to ensure they are up to date in tests or if env changes
    current_settings = get_settings()
    kwargs = {
        "QueueUrl": current_settings.sqs_queue_url,
        "MessageBody": msg.model_dump_json(by_alias=True),
    }
    # MessageGroupId is only for FIFO queues
    if current_settings.sqs_queue_url.endswith(".fifo"):
        kwargs["MessageGroupId"] = bucket

    sqs_client.send_message(**kwargs)


@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics
def lambda_handler(event: dict, context) -> dict:
    s3_event = _parse_event(event)
    success_count = 0
    errors = []

    for record in s3_event.records:
        try:
            bucket = record.s3.bucket.name
            key = record.s3.get_object.key
            event_time = record.event_time

            with tracer.provider.in_subsegment("process_record"):
                msg = _build_message(record)
                _publish(msg, bucket)
                logger.info("Processed record", extra={"bucket": bucket, "key": key, "event_time": event_time})
                success_count += 1
        except Exception as e:
            logger.error(f"Failed to process record: {e}", exc_info=True)
            metrics.add_metric(name="publish_failure", unit="Count", value=1)
            errors.append(e)

    metrics.add_metric(name="records_processed", unit="Count", value=success_count)

    if errors:
        # For S3 events, we should fail the whole batch if any record fails to ensure retry
        raise Exception(f"Batch processing failed with {len(errors)} errors. First error: {errors[0]}")

    return {"batchItemFailures": []}
