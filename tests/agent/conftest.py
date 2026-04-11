from boto3 import resource
from moto import mock_aws
from pytest import fixture

from templates.repository import Repository


@fixture
def table_name():
    return "test-table"


@fixture(autouse=True)
def mock_table(table_name):
    with mock_aws():
        yield resource("dynamodb").create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )


@fixture(autouse=True)
def repository(mock_table):
    return Repository(mock_table.table_name)
