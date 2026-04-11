from boto3 import client


class Queue:
    """Addresses all SQS interactions."""

    def __init__(self, queue_url: str, region_name: str = "us-east-1") -> None:
        """Initialize the SQS client.

        Args:
            queue_url: The URL of the SQS queue.
            region_name: The region to use.
        """
        self._queue_url = queue_url
        self._client = client("sqs", region_name=region_name)

    def publish(self, message: str) -> None:
        """Publish a processed message to SQS.

        Args:
            message: The message to publish.
        """
        self._client.send_message(QueueUrl=self._queue_url, MessageBody=message)
