from aws_cdk import RemovalPolicy, Stack
from aws_cdk.aws_lambda import Code, Function, Runtime
from aws_cdk.aws_lambda_event_sources import S3EventSource
from aws_cdk.aws_s3 import Bucket, EventType
from aws_cdk.aws_sqs import Queue
from constructs import Construct


class S3SqsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs: object) -> None:
        super().__init__(scope, construct_id, **kwargs)

        queue = Queue(
            self,
            "DestinationQueue",
        )

        bucket = Bucket(
            self,
            "SourceBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        function = Function(
            self,
            "S3SqsFunction",
            runtime=Runtime.PYTHON_3_13,
            handler="templates.s3.handler.main",
            code=Code.from_asset("."),
            environment={
                "SQS_QUEUE_URL": queue.queue_url,
                "POWERTOOLS_SERVICE_NAME": "s3-sqs-processor",
                "LOG_LEVEL": "INFO",
            },
        )

        queue.grant_send_messages(function)
        bucket.grant_read(function)

        function.add_event_source(
            S3EventSource(
                bucket,
                events=[EventType.OBJECT_CREATED],
            )
        )
