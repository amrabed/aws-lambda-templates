from unittest.mock import MagicMock

from aws_lambda_powertools.utilities.typing import LambdaContext
from pytest import fixture, main


@fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setenv("TABLE_NAME", "test-table")
    monkeypatch.setenv("POWERTOOLS_TRACE_DISABLED", "true")
    monkeypatch.setenv("POWERTOOLS_METRICS_DISABLED", "true")


@fixture
def mock_repository(mocker):
    mock = mocker.MagicMock()
    mocker.patch("templates.graphql.handler.get_repository", return_value=mock)
    return mock


@fixture
def lambda_context():
    ctx = MagicMock(spec=LambdaContext)
    ctx.function_name = "test-function"
    return ctx


def test_get_item_resolver(mock_repository, lambda_context):
    from templates.graphql.handler import main

    mock_repository.get_item.return_value = {"id": "123", "name": "Test Item"}
    event = {
        "info": {"parentTypeName": "Query", "fieldName": "getItem"},
        "arguments": {"id": "123"},
    }

    result = main(event, lambda_context)

    assert result == {"id": "123", "name": "Test Item"}
    mock_repository.get_item.assert_called_once_with("123")


def test_list_items_resolver(mock_repository, lambda_context):
    from templates.graphql.handler import main

    mock_repository.list_items.return_value = [{"id": "123", "name": "Test Item"}]
    event = {
        "info": {"parentTypeName": "Query", "fieldName": "listItems"},
        "arguments": {},
    }

    result = main(event, lambda_context)

    assert result == [{"id": "123", "name": "Test Item"}]
    mock_repository.list_items.assert_called_once()


def test_create_item_resolver(mock_repository, lambda_context):
    from templates.graphql.handler import main

    event = {
        "info": {"parentTypeName": "Mutation", "fieldName": "createItem"},
        "arguments": {"name": "New Item"},
    }

    result = main(event, lambda_context)

    assert result["name"] == "New Item"
    assert "id" in result
    mock_repository.put_item.assert_called_once()


if __name__ == "__main__":
    main()
