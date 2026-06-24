from boto3 import client
from botocore.config import Config


class Queue:
    """Addresses all SQS interactions."""

    def __init__(self, queue_url: str, region_name: str = "us-east-1") -> None:
        """Initialize the SQS client.

        Args:
            queue_url: The URL of the SQS queue.
            region_name: The region to use.
        """
        # Optimize connection resilience and performance with TCP keepalive and standard retries
        config = Config(tcp_keepalive=True, retries={"max_attempts": 3, "mode": "standard"})
        self._queue_url = queue_url
        self._client = client("sqs", region_name=region_name, config=config)

    def publish(self, message: str) -> None:
        """Publish a processed message to SQS.

        Args:
            message: The message to publish.
        """
        self._client.send_message(QueueUrl=self._queue_url, MessageBody=message)
