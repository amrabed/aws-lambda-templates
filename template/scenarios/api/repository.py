from __future__ import annotations

from typing import Any


class Repository:
    def __init__(self, table: Any) -> None:
        self._table = table

    def get_item(self, item_id: str) -> dict | None:
        response = self._table.get_item(Key={"id": item_id})
        return response.get("Item")

    def put_item(self, item: dict) -> None:
        self._table.put_item(Item=item)
