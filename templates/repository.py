from boto3 import resource


class Repository:
    """Manages all DynamoDB interactions for a single table."""

    def __init__(self, table_name: str) -> None:
        """Initialize the repository with a DynamoDB table.

        Args:
            table_name: The name of the DynamoDB table to operate on.
        """
        self._table = resource("dynamodb").Table(table_name)

    def get_item(self, item_id: str) -> dict | None:
        """Retrieve an item by its ID.

        Args:
            item_id: The unique identifier of the item to retrieve.

        Returns:
            The item as a dictionary, or `None` if not found.
        """
        return self._table.get_item(Key={"id": item_id}).get("Item")

    def list_items(self) -> list[dict]:
        """Retrieve all items from the table.

        Returns:
            A list of all items in the table.
        """
        return self._table.scan().get("Items", [])

    def put_item(self, item: dict) -> None:
        """Write an item to the table, replacing any existing item with the same key.

        Args:
            item: A dictionary representing the item to store.
        """
        self._table.put_item(Item=item)

    def delete_item(self, keys: object) -> None:
        """Delete an item from the table by its primary key.

        Args:
            keys: A mapping of key attribute names to their values.
        """
        self._table.delete_item(Key=keys)
