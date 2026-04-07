"""Unit tests for the stream handler."""

import importlib
import sys
from typing import Any
from unittest.mock import MagicMock, patch

from pytest import MonkeyPatch, fixture, main


@fixture()
def handler_module(monkeypatch: MonkeyPatch):
    """Set required env vars, then import the handler module fresh."""
    monkeypatch.setenv("SOURCE_TABLE_NAME", "source-table")
    monkeypatch.setenv("DESTINATION_TABLE_NAME", "dest-table")
    monkeypatch.setenv("SERVICE_NAME", "test-service")
    monkeypatch.setenv("METRICS_NAMESPACE", "test-namespace")
    monkeypatch.setenv("POWERTOOLS_SERVICE_NAME", "test-service")
    monkeypatch.setenv("POWERTOOLS_METRICS_NAMESPACE", "test-namespace")
    monkeypatch.setenv("POWERTOOLS_TRACE_DISABLED", "true")
    monkeypatch.setenv("POWERTOOLS_METRICS_DISABLED", "true")

    for mod_name in list(sys.modules.keys()):
        if "templates.stream" in mod_name or "templates.repository" in mod_name:
            del sys.modules[mod_name]

    mock_tracer_instance = MagicMock()
    mock_tracer_instance.capture_lambda_handler = lambda fn=None, **kw: (fn if fn else lambda f: f)
    mock_tracer_instance.capture_method = lambda fn=None, **kw: (fn if fn else lambda f: f)
    mock_tracer_cls = MagicMock(return_value=mock_tracer_instance)

    mock_dest_table = MagicMock()
    mock_dynamodb = MagicMock()
    mock_dynamodb.Table.return_value = mock_dest_table
    mock_boto3_resource = MagicMock(return_value=mock_dynamodb)

    with (
        patch("aws_lambda_powertools.Tracer", mock_tracer_cls),
        patch("boto3.resource", mock_boto3_resource),
    ):
        mod = importlib.import_module("templates.stream.handler")

    return mod


def _lambda_context() -> MagicMock:
    ctx = MagicMock()
    ctx.function_name = "test-function"
    ctx.memory_limit_in_mb = 128
    ctx.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    ctx.aws_request_id = "test-request-id"
    return ctx


def _stream_event(*records: dict) -> dict:
    return {"Records": list(records)}


def _insert_record(item_id: str = "abc", name: str = "Widget") -> dict:
    return {
        "eventName": "INSERT",
        "dynamodb": {
            "NewImage": {"id": {"S": item_id}, "name": {"S": name}},
            "Keys": {"id": {"S": item_id}},
            "SequenceNumber": f"seq-{item_id}",
        },
    }


def _modify_record(item_id: str = "abc", name: str = "Updated") -> dict:
    return {
        "eventName": "MODIFY",
        "dynamodb": {
            "NewImage": {"id": {"S": item_id}, "name": {"S": name}},
            "Keys": {"id": {"S": item_id}},
            "SequenceNumber": f"seq-{item_id}",
        },
    }


def _remove_record(item_id: str = "abc") -> dict:
    return {
        "eventName": "REMOVE",
        "dynamodb": {
            "Keys": {"id": {"S": item_id}},
            "SequenceNumber": f"seq-{item_id}",
        },
    }


def test_insert_record_calls_put_item(handler_module: Any, mocker: Any) -> None:
    """INSERT record: put_item is called with the deserialised NewImage."""
    mock_repo = MagicMock()
    handler_module.handler._repository = mock_repo

    event = _stream_event(_insert_record("abc", "Widget"))
    result = handler_module.main(event, _lambda_context())

    mock_repo.put_item.assert_called_once_with({"id": "abc", "name": "Widget"})
    mock_repo.delete_item.assert_not_called()
    assert result == {"batchItemFailures": []}


def test_modify_record_calls_put_item(handler_module: Any, mocker: Any) -> None:
    """MODIFY record: put_item is called with the deserialised NewImage."""
    mock_repo = MagicMock()
    handler_module.handler._repository = mock_repo

    event = _stream_event(_modify_record("abc", "Updated"))
    result = handler_module.main(event, _lambda_context())

    mock_repo.put_item.assert_called_once_with({"id": "abc", "name": "Updated"})
    mock_repo.delete_item.assert_not_called()
    assert result == {"batchItemFailures": []}


def test_remove_record_calls_delete_item(handler_module: Any, mocker: Any) -> None:
    """REMOVE record: delete_item is called with the deserialised key."""
    mock_repo = MagicMock()
    handler_module.handler._repository = mock_repo

    event = _stream_event(_remove_record("abc"))
    result = handler_module.main(event, _lambda_context())

    mock_repo.delete_item.assert_called_once_with({"id": "abc"})
    mock_repo.put_item.assert_not_called()
    assert result == {"batchItemFailures": []}


def test_deserialisation_failure_reports_batch_item_failure(handler_module: Any, mocker: Any) -> None:
    """A record with an invalid NewImage is reported as a batch item failure; processing continues."""
    mock_repo = MagicMock()
    handler_module.handler._repository = mock_repo

    bad_record = {
        "eventName": "INSERT",
        "dynamodb": {
            "NewImage": {"name": {"S": "NoId"}},
            "Keys": {"name": {"S": "NoId"}},
            "SequenceNumber": "seq-bad",
        },
    }
    good_record = _insert_record("ok", "Good")

    event = _stream_event(bad_record, good_record)
    result = handler_module.main(event, _lambda_context())

    mock_repo.put_item.assert_called_once_with({"id": "ok", "name": "Good"})
    assert len(result["batchItemFailures"]) == 1


def test_dynamodb_write_failure_reports_batch_item_failure(handler_module: Any, mocker: Any) -> None:
    """A repository put_item failure is reported; subsequent records are still processed."""
    mock_repo = MagicMock()
    mock_repo.put_item.side_effect = [Exception("DynamoDB unavailable"), None]
    handler_module.handler._repository = mock_repo

    event = _stream_event(_insert_record("fail", "Broken"), _insert_record("ok", "Fine"))
    result = handler_module.main(event, _lambda_context())

    assert mock_repo.put_item.call_count == 2
    assert len(result["batchItemFailures"]) == 1


if __name__ == "__main__":
    main()
