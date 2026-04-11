from json import dumps
from unittest.mock import MagicMock

from aws_lambda_powertools.utilities.typing import LambdaContext
from pytest import main

from templates.sqs.handler import Handler
from templates.sqs.handler import main as lambda_handler


def test_handler_handle_record(repository, table_name):
    handler = Handler(repository)
    record = MagicMock()
    record.body = dumps({"id": "123", "content": "test content"})

    handler.handle_record(record)

    item = repository.get_item("123")
    assert item is not None
    assert item["id"] == "123"
    assert item["content"] == "test content"
    assert item["status"] == "PROCESSED"


def test_lambda_handler(mocker, monkeypatch, repository, table_name):
    monkeypatch.setenv("TABLE_NAME", table_name)
    mocker.patch("templates.sqs.handler.Repository", return_value=repository)

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

    response = lambda_handler(event, context)

    assert response["batchItemFailures"] == []

    item = repository.get_item("123")
    assert item is not None
    assert item["content"] == "test 1"


if __name__ == "__main__":
    main()
