from boto3 import resource


class Repository:
    def __init__(self, table_name: str) -> None:
        self._table = resource("dynamodb").Table(table_name)

    def get_item(self, item_id: str) -> dict | None:
        return self._table.get_item(Key={"id": item_id}).get("Item")

    def put_item(self, item: dict) -> None:
        self._table.put_item(Item=item)

    def delete_item(self, keys: object) -> None:
        self._table.delete_item(Key=keys)
