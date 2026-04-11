from json import loads
from unittest.mock import MagicMock

from aws_lambda_powertools.utilities.typing import LambdaContext
from pytest import fixture, main


@fixture(autouse=True)
def env(monkeypatch) -> None:
    """Set required environment variables for the handler module."""
    monkeypatch.setenv("TABLE_NAME", "test-table")
    monkeypatch.setenv("POWERTOOLS_SERVICE_NAME", "test-service")
    monkeypatch.setenv("POWERTOOLS_METRICS_NAMESPACE", "test-namespace")
    monkeypatch.setenv("POWERTOOLS_METRICS_DISABLED", "true")
    monkeypatch.setenv("POWERTOOLS_TRACE_DISABLED", "true")


@fixture
def lambda_context():
    ctx = MagicMock(spec=LambdaContext)
    ctx.function_name = "test-function"
    ctx.memory_limit_in_mb = 128
    ctx.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    ctx.aws_request_id = "test-request-id"
    return ctx


@fixture
def bedrock_event():
    return {
        "messageVersion": "1.0",
        "agent": {"name": "TestAgent", "id": "AGENT123", "alias": "ALIAS123", "version": "DRAFT"},
        "inputText": "test input",
        "sessionId": "SESSION123",
        "actionGroup": "TestGroup",
        "sessionAttributes": {},
        "promptSessionAttributes": {},
    }


def test_handler_get_item(repository):
    from templates.agent.handler import get_item_logic

    repository.put_item({"id": "1", "name": "test item", "description": "test description"})

    result = get_item_logic("1")

    assert result["id"] == "1"
    assert result["name"] == "test item"
    assert result["description"] == "test description"


def test_handler_get_item_not_found(repository):
    from templates.agent.handler import get_item_logic

    result = get_item_logic("2")

    assert "error" in result
    assert "not found" in result["error"]


def test_handler_create_item(repository):
    from templates.agent.handler import create_item_logic

    result = create_item_logic("2", "new item", "new description")

    assert result["id"] == "2"
    assert result["name"] == "new item"
    assert result["description"] == "new description"

    item = repository.get_item("2")
    assert item is not None
    assert item["name"] == "new item"


def test_lambda_handler_get_item(mocker, repository, lambda_context, bedrock_event):
    from templates.agent.handler import main

    mocker.patch("templates.bedrock_agent.handler.repository", repository)
    repository.put_item({"id": "1", "name": "test item"})

    bedrock_event["function"] = "getItem"
    bedrock_event["parameters"] = [{"name": "item_id", "type": "string", "value": "1"}]

    response = main(bedrock_event, lambda_context)

    body = loads(response["response"]["functionResponse"]["responseBody"]["TEXT"]["body"])
    assert body == {"id": "1", "name": "test item"}


def test_lambda_handler_create_item(mocker, repository, lambda_context, bedrock_event):
    from templates.agent.handler import main

    mocker.patch("templates.bedrock_agent.handler.repository", repository)

    bedrock_event["function"] = "createItem"
    bedrock_event["parameters"] = [
        {"name": "item_id", "type": "string", "value": "2"},
        {"name": "name", "type": "string", "value": "new item"},
    ]

    response = main(bedrock_event, lambda_context)

    body = loads(response["response"]["functionResponse"]["responseBody"]["TEXT"]["body"])
    assert body["id"] == "2"
    assert body["name"] == "new item"


if __name__ == "__main__":
    main()
