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


if __name__ == "__main__":
    main()
