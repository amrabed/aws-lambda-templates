"""Unit tests for the stream Repository class.

Requirements: 6.4, 9.3
"""
from __future__ import annotations

from unittest.mock import MagicMock

from template.scenarios.stream.repository import Repository


def test_put_item_calls_table() -> None:
    """put_item calls the destination DynamoDB table with the correct Item."""
    mock_table = MagicMock()
    repo = Repository(mock_table)

    repo.put_item({"id": "abc", "name": "Widget"})

    mock_table.put_item.assert_called_once_with(Item={"id": "abc", "name": "Widget"})


def test_delete_item_calls_table() -> None:
    """delete_item calls the destination DynamoDB table with the correct Key."""
    mock_table = MagicMock()
    repo = Repository(mock_table)

    repo.delete_item({"id": "abc"})

    mock_table.delete_item.assert_called_once_with(Key={"id": "abc"})
