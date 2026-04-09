import boto3

from templates.s3.models import ProcessedMessage
from templates.s3.settings import Settings


class Queue:
    """Addresses all SQS interactions."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the SQS client.

        Args:
            settings: The application settings containing SQS configuration.
        """
        self._queue_url = settings.sqs_queue_url
        self._client = boto3.client("sqs", region_name=settings.aws_region)
        self._is_fifo = self._queue_url.endswith(".fifo")

    def publish(self, message: ProcessedMessage, group_id: str) -> None:
        """Publish a processed message to SQS.

        Args:
            message: The message to publish.
            group_id: The MessageGroupId to use (only for FIFO queues).
        """
        kwargs = {
            "QueueUrl": self._queue_url,
            "MessageBody": message.model_dump_json(by_alias=True),
        }
        if self._is_fifo:
            kwargs["MessageGroupId"] = group_id

        self._client.send_message(**kwargs)
