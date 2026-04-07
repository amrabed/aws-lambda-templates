from __future__ import annotations

from typing import Any


class Repository:
    def __init__(self, destination_table: Any) -> None:
        self._destination_table = destination_table

    def put_item(self, item: dict) -> None:
        self._destination_table.put_item(Item=item)

    def delete_item(self, key: dict) -> None:
        self._destination_table.delete_item(Key=key)
