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


def test_handler_get_item(repository):
    from templates.bedrock_agent.handler import Handler

    handler = Handler(repository)
    repository.put_item({"id": "1", "name": "test item", "description": "test description"})

    result = handler.get_item("1")

    assert result["id"] == "1"
    assert result["name"] == "test item"
    assert result["description"] == "test description"


def test_handler_get_item_not_found(repository):
    from templates.bedrock_agent.handler import Handler

    handler = Handler(repository)

    result = handler.get_item("2")

    assert "error" in result
    assert "not found" in result["error"]


def test_handler_create_item(repository):
    from templates.bedrock_agent.handler import Handler

    handler = Handler(repository)

    result = handler.create_item("2", "new item", "new description")

    assert result["id"] == "2"
    assert result["name"] == "new item"
    assert result["description"] == "new description"

    item = repository.get_item("2")
    assert item is not None
    assert item["name"] == "new item"


def test_lambda_handler_get_item(mocker, monkeypatch, repository, table_name):
    from templates.bedrock_agent.handler import main

    monkeypatch.setenv("TABLE_NAME", table_name)
    mocker.patch("templates.bedrock_agent.handler.Repository", return_value=repository)
    repository.put_item({"id": "1", "name": "test item"})

    event = {
        "messageVersion": "1.0",
        "agent": {"name": "TestAgent", "id": "AGENT123", "alias": "ALIAS123", "version": "DRAFT"},
        "inputText": "Get item 1",
        "sessionId": "SESSION123",
        "actionGroup": "TestGroup",
        "function": "getItem",
        "parameters": [{"name": "item_id", "type": "string", "value": "1"}],
    }
    context = MagicMock(spec=LambdaContext)

    response = main(event, context)

    assert loads(response["response"]["functionResponse"]["responseBody"]["TEXT"]["body"]) == {
        "id": "1",
        "name": "test item",
    }


def test_lambda_handler_create_item(mocker, monkeypatch, repository, table_name):
    from templates.bedrock_agent.handler import main

    monkeypatch.setenv("TABLE_NAME", table_name)
    mocker.patch("templates.bedrock_agent.handler.Repository", return_value=repository)

    event = {
        "messageVersion": "1.0",
        "agent": {"name": "TestAgent", "id": "AGENT123", "alias": "ALIAS123", "version": "DRAFT"},
        "inputText": "Create item 2",
        "sessionId": "SESSION123",
        "actionGroup": "TestGroup",
        "function": "createItem",
        "parameters": [
            {"name": "item_id", "type": "string", "value": "2"},
            {"name": "name", "type": "string", "value": "new item"},
        ],
    }
    context = MagicMock(spec=LambdaContext)

    response = main(event, context)

    body = loads(response["response"]["functionResponse"]["responseBody"]["TEXT"]["body"])
    assert body["id"] == "2"
    assert body["name"] == "new item"


if __name__ == "__main__":
    main()
