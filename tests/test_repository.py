"""Unit tests for the DynamoDB repository"""

from boto3 import resource
from moto import mock_aws
from pytest import fixture, main

from templates.repository import Repository

_TABLE_NAME: str = "test-table"


@fixture
def mock_table():
    with mock_aws():
        yield resource("dynamodb").create_table(
            TableName=_TABLE_NAME,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )


@fixture()
def repository(mock_table):
    return Repository(_TABLE_NAME)


def test_get_item_returns_item(repository, mock_table):
    """get_item returns the Item value from the DynamoDB response"""
    mock_table.put_item(Item={"id": "abc", "name": "Widget"})
    assert repository.get_item("abc") == {"id": "abc", "name": "Widget"}


def test_get_item_returns_none_when_missing(repository):
    """get_item returns None when the item is not in DynamoDB"""
    assert repository.get_item("missing") is None


def test_put_item_calls_table(repository, mock_table):
    """put_item calls the DynamoDB table with the correct Item"""
    repository.put_item({"id": "xyz", "name": "Gadget"})

    assert mock_table.get_item(Key={"id": "xyz"}).get("Item") == {"id": "xyz", "name": "Gadget"}


if __name__ == "__main__":
    main()
