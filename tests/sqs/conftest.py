from moto import mock_aws
from pytest import fixture

from templates.repository import Repository


@fixture
def table_name():
    return "test-table"


@fixture(autouse=True)
def env(monkeypatch, table_name):
    monkeypatch.setenv("TABLE_NAME", table_name)


@fixture
def repository(table_name):
    from boto3 import resource

    with mock_aws():
        resource("dynamodb", region_name="us-east-1").create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield Repository(table_name)
