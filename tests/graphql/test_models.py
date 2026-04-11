from templates.graphql.models import Item


def test_item_model_defaults():
    item = Item(name="Test Item")
    assert item.id is not None
    assert item.name == "Test Item"


def test_item_model_dump():
    item = Item(id="123", name="Test Item")
    dump = item.dump()
    assert dump["id"] == "123"
    assert dump["name"] == "Test Item"
