from pytest import fixture, main


@fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setenv("TABLE_NAME", "test-table")
    monkeypatch.setenv("POWERTOOLS_TRACE_DISABLED", "true")
    monkeypatch.setenv("POWERTOOLS_METRICS_DISABLED", "true")


@fixture
def item():
    return {"id": "123", "name": "Test Item"}


@fixture
def test_get_item_resolver(repository, item, lambda_context):
    from templates.graphql.handler import main

    event = {"info": {"parentTypeName": "Query", "fieldName": "getItem"}, "arguments": {"id": "123"}}
    repository.put_item(item)
    assert main(event, lambda_context) == item


def test_list_items_resolver(repository, item, lambda_context):
    from templates.graphql.handler import main

    event = {"info": {"parentTypeName": "Query", "fieldName": "listItems"}, "arguments": {}}
    repository.put_item(item)
    assert main(event, lambda_context) == [item]


def test_create_item_resolver(lambda_context):
    from templates.graphql.handler import main

    event = {"info": {"parentTypeName": "Mutation", "fieldName": "createItem"}, "arguments": {"name": "New Item"}}

    result = main(event, lambda_context)
    assert result["name"] == "New Item"
    assert "id" in result


def test_sensitive_data_exposure(repository, lambda_context):
    """Verify that internal fields in DynamoDB are NOT leaked to the client."""
    from templates.graphql.handler import main

    item_with_secret = {"id": "123", "name": "Test Item", "internal_secret": "TOP_SECRET"}
    repository.put_item(item_with_secret)

    # Test getItem
    event_get = {"info": {"parentTypeName": "Query", "fieldName": "getItem"}, "arguments": {"id": "123"}}
    result_get = main(event_get, lambda_context)
    assert "internal_secret" not in result_get

    # Test listItems
    event_list = {"info": {"parentTypeName": "Query", "fieldName": "listItems"}, "arguments": {}}
    result_list = main(event_list, lambda_context)
    assert "internal_secret" not in result_list[0]


def test_error_message_information_leakage(lambda_context, mocker):
    """Verify that internal error details are NOT leaked to the client."""
    from templates.graphql import handler
    from templates.graphql.handler import get_item

    mocker.patch.object(handler.repository, "get_item", side_effect=Exception("Database connection failed"))

    import pytest

    with pytest.raises(RuntimeError) as excinfo:
        get_item("123")

    assert "Database connection failed" not in str(excinfo.value)
    assert "Cause:" not in str(excinfo.value)


if __name__ == "__main__":
    main()
