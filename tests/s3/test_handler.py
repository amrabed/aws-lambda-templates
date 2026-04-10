from json import loads
from uuid import uuid4

from aws_lambda_powertools.utilities.data_classes import S3Event
from hypothesis import HealthCheck, given, settings
from hypothesis.strategies import datetimes, fixed_dictionaries, from_regex, lists, text
from moto import mock_aws
from pytest import fixture, main, raises


class MockContext:
    def __init__(self):
        self.function_name = "test-function"
        self.memory_limit_in_mb = 128
        self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
        self.aws_request_id = "test-request-id"


@fixture
def lambda_context():
    return MockContext()


@fixture
def sqs():
    from boto3 import client

    with mock_aws():
        yield client("sqs", region_name="us-east-1")


@fixture(autouse=True)
def queue_url(monkeypatch, sqs):
    # Use a standard queue to avoid deduplication in property tests that expect multiple messages
    url = sqs.create_queue(QueueName="test-queue")["QueueUrl"]
    monkeypatch.setenv("SQS_QUEUE_URL", url)
    yield url


@fixture
def event():
    return S3Event(
        {
            "Records": [
                {
                    "eventTime": "2025-01-15T10:30:00Z",
                    "s3": {"bucket": {"name": "test-bucket"}, "object": {"key": "test-key"}},
                }
            ]
        }
    )


def test_handler_zero_records(sqs, monkeypatch, lambda_context, queue_url):
    from templates.s3.handler import main

    assert main(S3Event({"Records": []}), lambda_context) == {"batchItemFailures": []}  # type: ignore
    assert len(sqs.receive_message(QueueUrl=queue_url).get("Messages", [])) == 0


def test_handler_single_valid_record(sqs, monkeypatch, lambda_context, queue_url, event):
    from templates.s3.handler import main

    assert main(event, lambda_context) == {"batchItemFailures": []}  # type: ignore

    messages = sqs.receive_message(QueueUrl=queue_url).get("Messages", [])
    assert len(messages) == 1
    body = loads(messages[0]["Body"])
    assert body["bucket"] == "test-bucket"
    assert body["key"] == "test-key"


def test_handler_sqs_publish_failure(sqs, monkeypatch, mocker, lambda_context, queue_url, event):
    from templates.s3.handler import main, queue

    # Mock sqs_client.send_message to raise an exception
    mocker.patch.object(queue._client, "send_message", side_effect=Exception("SQS error"))

    with raises(Exception, match="Batch processing failed"):
        main(event, lambda_context)  # type: ignore


# --- Helpers for S3 record strategy ---
s3_bucket_name_strategy = from_regex(r"^[a-z0-9.-]{3,63}$", fullmatch=True)
s3_key_strategy = text(min_size=1, max_size=100).filter(lambda x: "\n" not in x and "\r" not in x)
s3_record_strategy = fixed_dictionaries(
    {
        "eventTime": datetimes().map(lambda x: x.isoformat() + "Z"),
        "s3": fixed_dictionaries(
            {
                "bucket": fixed_dictionaries({"name": s3_bucket_name_strategy}),
                "object": fixed_dictionaries({"key": s3_key_strategy}),
            }
        ),
    }
)


@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(records=lists(s3_record_strategy, min_size=1, max_size=20))
def test_property_record_count_preservation(sqs, records, queue_url):
    from templates.s3.handler import main

    main(S3Event({"Records": records}), MockContext())  # type: ignore

    # Count messages in SQS queue
    messages = []
    while len(messages) < len(records):
        response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=0)
        if "Messages" not in response:
            break
        messages.extend(response["Messages"])
        for m in response["Messages"]:
            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=m["ReceiptHandle"])

    assert len(messages) == len(records)


@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(records=lists(s3_record_strategy, min_size=1, max_size=10))
def test_property_partial_batch_failure_independence(sqs, mocker, records, queue_url):
    from templates.s3.handler import main, queue

    # Fail for records where key length is even
    original_send_message = queue._client.send_message

    def side_effect(*args, **kwargs):
        body = loads(kwargs["MessageBody"])
        if len(body["key"]) % 2 == 0:
            raise Exception("Simulated SQS failure")
        return original_send_message(*args, **kwargs)

    mocker.patch.object(queue._client, "send_message", side_effect=side_effect)

    event = S3Event({"Records": records})

    any_fail = any(len(r["s3"]["object"]["key"]) % 2 == 0 for r in records)

    if any_fail:
        with raises(Exception, match="Batch processing failed"):
            main(event, MockContext())  # type: ignore
    else:
        main(event, MockContext())  # type: ignore

    success_keys = [r["s3"]["object"]["key"] for r in records if len(r["s3"]["object"]["key"]) % 2 != 0]

    messages = []
    while len(messages) < len(success_keys):
        response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=0)
        if "Messages" not in response:
            break
        messages.extend(response["Messages"])
        for m in response["Messages"]:
            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=m["ReceiptHandle"])

    assert len(messages) == len(success_keys)


@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(records=lists(s3_record_strategy, min_size=1, max_size=5))
def test_property_non_idempotent_double_invocation(sqs, records, queue_url):
    from templates.s3.handler import main

    event = S3Event({"Records": records})
    context = MockContext()
    main(event, context)  # type: ignore
    main(event, context)  # type: ignore

    messages = []
    while len(messages) < 2 * len(records):
        response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=0)
        if "Messages" not in response:  # no more messages in the queue
            break
        messages.extend(response["Messages"])
        for message in response["Messages"]:
            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"])

    assert len(messages) == 2 * len(records)


@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(records=lists(s3_record_strategy, min_size=1, max_size=10))
def test_property_records_processed_metric_equals_success_count(sqs, mocker, records, queue_url):
    from templates.s3 import handler
    from templates.s3.handler import main, queue

    # Mock Metrics
    mock_metrics = mocker.patch.object(handler, "metrics")

    def side_effect(*args, **kwargs):  # noqa
        if len(loads(kwargs["MessageBody"])["key"]) % 2 == 0:  # Fail for records where key length is even
            raise Exception("Simulated SQS failure")
        return {"MessageId": "123"}

    mocker.patch.object(queue._client, "send_message", side_effect=side_effect)

    event = S3Event({"Records": records})

    any_failure = any(len(r["s3"]["object"]["key"]) % 2 == 0 for r in records)
    if any_failure:
        with raises(Exception):
            main(event, MockContext())  # type: ignore
    else:
        main(event, MockContext())  # type: ignore

    success_count = len([r for r in records if len(r["s3"]["object"]["key"]) % 2 != 0])

    calls = mock_metrics.add_metric.call_args_list
    processed_call = [c for c in calls if c.kwargs.get("name") == "records_processed"]
    assert len(processed_call) == 1
    assert processed_call[0].kwargs.get("value") == success_count


if __name__ == "__main__":
    main()
