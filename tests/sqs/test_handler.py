from json import dumps
from unittest.mock import MagicMock

from aws_lambda_powertools.utilities.typing import LambdaContext
from pytest import fixture, main


@fixture(autouse=True)
def env(monkeypatch, table_name):
    monkeypatch.setenv("TABLE_NAME", table_name)


def test_handler_handle_record(provider):
    from templates.sqs.handler import Handler

    handler = Handler(provider)
    record = MagicMock()
    record.json_body = {"id": "123", "content": "test content"}

    handler.handle_record(record)

    item = provider.table.get_item(Key={"id": "123"}).get("Item")
    assert item is not None
    assert item["id"] == "123"
    assert item["content"] == "test content"
    assert item["status"] == "PROCESSED"


def test_lambda_handler(mocker, monkeypatch, provider, table_name):
    from templates.sqs.handler import main

    monkeypatch.setenv("TABLE_NAME", table_name)
    mocker.patch("templates.sqs.handler.provider", provider)

    event = {
        "Records": [
            {
                "messageId": "1",
                "receiptHandle": "abc",
                "body": dumps({"id": "123", "content": "test 1"}),
                "attributes": {},
                "messageAttributes": {},
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:queue",
                "awsRegion": "us-east-1",
            }
        ]
    }

    context = MagicMock(spec=LambdaContext)

    response = main(event, context)

    assert response["batchItemFailures"] == []

    item = provider.table.get_item(Key={"id": "123"}).get("Item")
    assert item is not None
    assert item["content"] == "test 1"


if __name__ == "__main__":
    main()
