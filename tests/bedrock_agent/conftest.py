from boto3 import resource
from moto import mock_aws
from pytest import fixture

from templates.repository import Repository

_TABLE_NAME = "test-table"


@fixture
def table_name():
    return _TABLE_NAME


@fixture
def mock_table():
    with mock_aws():
        yield resource("dynamodb").create_table(
            TableName=_TABLE_NAME,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )


@fixture
def repository(mock_table):
    return Repository(_TABLE_NAME)
