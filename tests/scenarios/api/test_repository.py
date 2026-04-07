"""Unit tests for the api Repository class.

Requirements: 6.4, 9.3
"""
from __future__ import annotations

from unittest.mock import MagicMock

from template.scenarios.api.repository import Repository


def test_get_item_returns_item() -> None:
    """get_item returns the Item value from the DynamoDB response."""
    mock_table = MagicMock()
    mock_table.get_item.return_value = {"Item": {"id": "abc", "name": "Widget"}}

    repo = Repository(mock_table)
    result = repo.get_item("abc")

    assert result == {"id": "abc", "name": "Widget"}
    mock_table.get_item.assert_called_once_with(Key={"id": "abc"})


def test_get_item_returns_none_when_missing() -> None:
    """get_item returns None when the item is not in DynamoDB."""
    mock_table = MagicMock()
    mock_table.get_item.return_value = {}

    repo = Repository(mock_table)
    result = repo.get_item("missing")

    assert result is None


def test_put_item_calls_table() -> None:
    """put_item calls the DynamoDB table with the correct Item."""
    mock_table = MagicMock()
    repo = Repository(mock_table)

    repo.put_item({"id": "xyz", "name": "Gadget"})

    mock_table.put_item.assert_called_once_with(Item={"id": "xyz", "name": "Gadget"})
