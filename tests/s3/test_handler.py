import json
import os
import uuid
from unittest.mock import MagicMock

import boto3
import pytest
from hypothesis import HealthCheck, given
from hypothesis import settings as hypothesis_settings
from hypothesis import strategies as st
from moto import mock_aws
from pydantic import ValidationError
from pytest import fixture

# Environment must be set before any templates.s3 imports to avoid validation errors at module load
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["SQS_QUEUE_URL"] = "https://sqs.us-east-1.amazonaws.com/123456789012/test-queue"

from templates.s3.handler import handler, main
from templates.s3.models import EventSource, ProcessedMessage
from templates.s3.queue import Queue
from templates.s3.settings import Settings


class MockContext:
    def __init__(self):
        self.function_name = "test-function"
        self.memory_limit_in_mb = 128
        self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
        self.aws_request_id = "test-request-id"


@fixture(autouse=True)
def env(monkeypatch) -> None:
    """Set required environment variables for the handler module."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("SQS_QUEUE_URL", "https://sqs.us-east-1.amazonaws.com/123456789012/test-queue")
    monkeypatch.setenv("POWERTOOLS_SERVICE_NAME", "s3-sqs-processor")
    monkeypatch.setenv("POWERTOOLS_METRICS_DISABLED", "true")
    monkeypatch.setenv("POWERTOOLS_TRACE_DISABLED", "true")


@fixture
def sqs(env):
    with mock_aws():
        yield boto3.client("sqs", region_name="us-east-1")


@fixture
def lambda_context():
    return MockContext()


def test_settings_defaults(monkeypatch):
    monkeypatch.setenv("SQS_QUEUE_URL", "https://sqs.us-east-1.amazonaws.com/123456789012/my-queue")
    settings = Settings()  # type: ignore
    assert settings.sqs_queue_url == "https://sqs.us-east-1.amazonaws.com/123456789012/my-queue"
    assert settings.aws_region == "us-east-1"
    assert settings.powertools_service_name == "s3-sqs-processor"
    assert settings.log_level == "INFO"


def test_settings_validation(monkeypatch):
    monkeypatch.delenv("SQS_QUEUE_URL", raising=False)
    with pytest.raises(ValidationError):
        Settings()  # type: ignore


def test_build_message_correctness():
    class MockRecord:
        class MockS3:
            class MockBucket:
                name = "test-bucket"

            class MockObject:
                key = "test-key"

            bucket = MockBucket()
            get_object = MockObject()

        s3 = MockS3()
        event_time = "2025-01-15T10:30:00Z"

    record = MockRecord()
    msg = handler._build_message(record)  # type: ignore
    assert msg.bucket == "test-bucket"
    assert msg.key == "test-key"
    assert msg.event_time == "2025-01-15T10:30:00Z"
    assert msg.source == EventSource.s3


def test_handler_zero_records(sqs, monkeypatch, lambda_context):
    queue_url = sqs.create_queue(QueueName="test-queue")["QueueUrl"]
    monkeypatch.setenv("SQS_QUEUE_URL", queue_url)
    handler._queue = Queue(Settings())  # type: ignore

    event = {"Records": []}
    result = main(event, lambda_context)  # type: ignore

    assert result == {"batchItemFailures": []}
    messages = sqs.receive_message(QueueUrl=queue_url).get("Messages", [])
    assert len(messages) == 0


def test_handler_single_valid_record(sqs, monkeypatch, lambda_context):
    queue_url = sqs.create_queue(
        QueueName="test-queue.fifo", Attributes={"FifoQueue": "true", "ContentBasedDeduplication": "true"}
    )["QueueUrl"]
    monkeypatch.setenv("SQS_QUEUE_URL", queue_url)
    handler._queue = Queue(Settings())  # type: ignore

    event = {
        "Records": [
            {
                "eventTime": "2025-01-15T10:30:00Z",
                "s3": {"bucket": {"name": "test-bucket"}, "object": {"key": "test-key"}},
            }
        ]
    }

    result = main(event, lambda_context)  # type: ignore
    assert result == {"batchItemFailures": []}

    messages = sqs.receive_message(QueueUrl=queue_url, AttributeNames=["MessageGroupId"]).get("Messages", [])
    assert len(messages) == 1
    body = json.loads(messages[0]["Body"])
    assert body["bucket"] == "test-bucket"
    assert body["key"] == "test-key"
    assert messages[0]["Attributes"]["MessageGroupId"] == "test-bucket"


def test_handler_sqs_publish_failure(sqs, monkeypatch, mocker, lambda_context):
    queue_url = "https://sqs.us-east-1.amazonaws.com/123456789012/test-queue"
    monkeypatch.setenv("SQS_QUEUE_URL", queue_url)
    handler._queue = Queue(Settings())  # type: ignore

    # Mock sqs_client.send_message to raise an exception
    mocker.patch.object(handler._queue._client, "send_message", side_effect=Exception("SQS error"))

    event = {
        "Records": [
            {
                "eventTime": "2025-01-15T10:30:00Z",
                "s3": {"bucket": {"name": "test-bucket"}, "object": {"key": "test-key"}},
            }
        ]
    }

    with pytest.raises(Exception, match="Batch processing failed"):
        main(event, lambda_context)  # type: ignore


# Property-based tests


# Feature: s3-sqs-lambda-template, Property 4: ProcessedMessage serialization round-trip
@hypothesis_settings(max_examples=100, deadline=None)
@given(st.builds(ProcessedMessage))
def test_property_processed_message_serialization_round_trip(msg):
    json_data = msg.model_dump_json(by_alias=True)
    parsed_msg = ProcessedMessage.model_validate_json(json_data)
    assert msg == parsed_msg


# Feature: s3-sqs-lambda-template, Property 3: Missing SQS_QUEUE_URL raises ValidationError
@hypothesis_settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(queue_url=st.one_of(st.just(None), st.just("")))
def test_property_missing_sqs_queue_url_raises_validation_error(monkeypatch, queue_url):
    with monkeypatch.context() as m:
        if queue_url is None:
            m.delenv("SQS_QUEUE_URL", raising=False)
        else:
            m.setenv("SQS_QUEUE_URL", queue_url)
        with pytest.raises(ValidationError):
            Settings()  # type: ignore


# Helper for S3 record strategy
s3_bucket_name_strategy = st.from_regex(r"^[a-z0-9.-]{3,63}$", fullmatch=True)
s3_key_strategy = st.text(min_size=1, max_size=100).filter(lambda x: "\n" not in x and "\r" not in x)

s3_record_strategy = st.fixed_dictionaries(
    {
        "eventTime": st.datetimes().map(lambda x: x.isoformat() + "Z"),
        "s3": st.fixed_dictionaries(
            {
                "bucket": st.fixed_dictionaries({"name": s3_bucket_name_strategy}),
                "object": st.fixed_dictionaries({"key": s3_key_strategy}),
            }
        ),
    }
)


# Feature: s3-sqs-lambda-template, Property 1: Record count preservation
@hypothesis_settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(records=st.lists(s3_record_strategy, min_size=1, max_size=20))
def test_property_record_count_preservation(sqs, monkeypatch, records):
    # Use a unique queue name to avoid state leakage between examples
    queue_name = f"test-queue-{uuid.uuid4().hex}"
    queue_url = sqs.create_queue(QueueName=queue_name)["QueueUrl"]
    monkeypatch.setenv("SQS_QUEUE_URL", queue_url)
    handler._queue = Queue(Settings())  # type: ignore

    event = {"Records": records}
    main(event, MockContext())  # type: ignore

    messages = []
    while len(messages) < len(records):
        resp = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=0)
        if "Messages" not in resp:
            break
        messages.extend(resp["Messages"])
        for m in resp["Messages"]:
            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=m["ReceiptHandle"])

    assert len(messages) == len(records)


# Feature: s3-sqs-lambda-template, Property 2: Invalid event raises ValueError
@hypothesis_settings(max_examples=100, deadline=None)
@given(event=st.dictionaries(st.text(), st.text()))
def test_property_invalid_event_raises_value_error(event):
    # Only if it's not a valid S3 event structure
    if "Records" in event and isinstance(event["Records"], list):
        return
    with pytest.raises(ValueError):
        main(event, MockContext())  # type: ignore


# Feature: s3-sqs-lambda-template, Property 5: MessageGroupId equals bucket name
@hypothesis_settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(record=s3_record_strategy)
def test_property_message_group_id_equals_bucket_name(sqs, monkeypatch, record):
    bucket_name = record["s3"]["bucket"]["name"]
    queue_name = f"test-queue-{uuid.uuid4().hex}.fifo"
    queue_attr = {"FifoQueue": "true", "ContentBasedDeduplication": "true"}
    queue_url = sqs.create_queue(QueueName=queue_name, Attributes=queue_attr)["QueueUrl"]
    monkeypatch.setenv("SQS_QUEUE_URL", queue_url)
    handler._queue = Queue(Settings())  # type: ignore

    event = {"Records": [record]}
    main(event, MockContext())  # type: ignore

    resp = sqs.receive_message(QueueUrl=queue_url, AttributeNames=["MessageGroupId"])
    if "Messages" in resp:
        assert resp["Messages"][0]["Attributes"]["MessageGroupId"] == bucket_name


# Feature: s3-sqs-lambda-template, Property 6: Partial batch failure independence
@hypothesis_settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(records=st.lists(s3_record_strategy, min_size=1, max_size=10))
def test_property_partial_batch_failure_independence(sqs, monkeypatch, mocker, records):
    queue_name = f"test-queue-{uuid.uuid4().hex}"
    queue_url = sqs.create_queue(QueueName=queue_name)["QueueUrl"]
    monkeypatch.setenv("SQS_QUEUE_URL", queue_url)
    handler._queue = Queue(Settings())  # type: ignore

    # Fail for records where key length is even
    original_send_message = handler._queue._client.send_message

    def side_effect(*args, **kwargs):
        body = json.loads(kwargs["MessageBody"])
        if len(body["key"]) % 2 == 0:
            raise Exception("Simulated SQS failure")
        return original_send_message(*args, **kwargs)

    mocker.patch.object(handler._queue._client, "send_message", side_effect=side_effect)

    event = {"Records": records}

    any_fail = any(len(r["s3"]["object"]["key"]) % 2 == 0 for r in records)

    if any_fail:
        with pytest.raises(Exception, match="Batch processing failed"):
            main(event, MockContext())  # type: ignore
    else:
        main(event, MockContext())  # type: ignore

    success_keys = [r["s3"]["object"]["key"] for r in records if len(r["s3"]["object"]["key"]) % 2 != 0]

    messages = []
    while len(messages) < len(success_keys):
        resp = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=0)
        if "Messages" not in resp:
            break
        messages.extend(resp["Messages"])
        for m in resp["Messages"]:
            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=m["ReceiptHandle"])

    assert len(messages) == len(success_keys)


# Feature: s3-sqs-lambda-template, Property 7: Non-idempotent double invocation
@hypothesis_settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(records=st.lists(s3_record_strategy, min_size=1, max_size=5))
def test_property_non_idempotent_double_invocation(sqs, monkeypatch, records):
    queue_name = f"test-queue-{uuid.uuid4().hex}"
    queue_url = sqs.create_queue(QueueName=queue_name)["QueueUrl"]
    monkeypatch.setenv("SQS_QUEUE_URL", queue_url)
    handler._queue = Queue(Settings())  # type: ignore

    event = {"Records": records}
    ctx = MockContext()
    main(event, ctx)  # type: ignore
    main(event, ctx)  # type: ignore

    messages = []
    while len(messages) < 2 * len(records):
        resp = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=0)
        if "Messages" not in resp:
            break
        messages.extend(resp["Messages"])
        for m in resp["Messages"]:
            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=m["ReceiptHandle"])

    assert len(messages) == 2 * len(records)


# Feature: s3-sqs-lambda-template, Property 8: records_processed metric equals success count
@hypothesis_settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(records=st.lists(s3_record_strategy, min_size=1, max_size=10))
def test_property_records_processed_metric_equals_success_count(sqs, monkeypatch, mocker, records):
    queue_name = f"test-queue-{uuid.uuid4().hex}"
    queue_url = sqs.create_queue(QueueName=queue_name)["QueueUrl"]
    monkeypatch.setenv("SQS_QUEUE_URL", queue_url)
    handler._queue = Queue(Settings())  # type: ignore

    # Mock Metrics
    import templates.s3.handler

    mock_metrics = mocker.patch.object(templates.s3.handler, "metrics")

    # Fail for records where key length is even
    def side_effect(*args, **kwargs):
        body = json.loads(kwargs["MessageBody"])
        if len(body["key"]) % 2 == 0:
            raise Exception("Simulated SQS failure")
        return {"MessageId": "123"}

    mocker.patch.object(handler._queue._client, "send_message", side_effect=side_effect)

    event = {"Records": records}

    any_fail = any(len(r["s3"]["object"]["key"]) % 2 == 0 for r in records)
    if any_fail:
        with pytest.raises(Exception):
            main(event, MockContext())  # type: ignore
    else:
        main(event, MockContext())  # type: ignore

    success_count = len([r for r in records if len(r["s3"]["object"]["key"]) % 2 != 0])

    calls = mock_metrics.add_metric.call_args_list
    processed_call = [c for c in calls if c.kwargs.get("name") == "records_processed"]
    assert len(processed_call) == 1
    assert processed_call[0].kwargs.get("value") == success_count


if __name__ == "__main__":
    from pytest import main as run_tests

    run_tests()
