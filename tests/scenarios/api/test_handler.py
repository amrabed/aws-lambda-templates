"""Unit tests for the api handler.

Requirements: 9.1, 9.2, 9.4
"""
from __future__ import annotations

import importlib
import json
import sys
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture()
def handler_module(monkeypatch: pytest.MonkeyPatch):
    """Set required env vars, then import (or reload) the handler module fresh."""
    monkeypatch.setenv("TABLE_NAME", "test-table")
    monkeypatch.setenv("SERVICE_NAME", "test-service")
    monkeypatch.setenv("METRICS_NAMESPACE", "test-namespace")
    monkeypatch.setenv("POWERTOOLS_SERVICE_NAME", "test-service")
    monkeypatch.setenv("POWERTOOLS_METRICS_NAMESPACE", "test-namespace")
    monkeypatch.setenv("POWERTOOLS_METRICS_DISABLED", "true")

    for mod_name in list(sys.modules.keys()):
        if "template.scenarios.api" in mod_name:
            del sys.modules[mod_name]

    mock_tracer_instance = MagicMock()
    mock_tracer_instance.capture_lambda_handler = lambda fn=None, **kw: (fn if fn else lambda f: f)
    mock_tracer_cls = MagicMock(return_value=mock_tracer_instance)

    mock_table = MagicMock()
    mock_dynamodb = MagicMock()
    mock_dynamodb.Table.return_value = mock_table
    mock_boto3_resource = MagicMock(return_value=mock_dynamodb)

    with (
        patch("aws_lambda_powertools.Tracer", mock_tracer_cls),
        patch("boto3.resource", mock_boto3_resource),
    ):
        mod = importlib.import_module("template.scenarios.api.handler")

    return mod


def _apigw_event(method: str, path: str, path_params: dict[str, str] | None = None, body: Any = None) -> dict:
    return {
        "version": "1.0",
        "httpMethod": method,
        "path": path,
        "pathParameters": path_params or {},
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "headers": {"Content-Type": "application/json"},
        "multiValueHeaders": {},
        "body": json.dumps(body) if body is not None else None,
        "isBase64Encoded": False,
        "requestContext": {
            "resourcePath": path,
            "httpMethod": method,
            "path": path,
            "stage": "test",
            "requestId": "test-request-id",
            "identity": {"sourceIp": "127.0.0.1", "userAgent": "pytest"},
            "accountId": "123456789012",
        },
        "resource": path,
        "stageVariables": None,
    }


def _lambda_context() -> MagicMock:
    ctx = MagicMock()
    ctx.function_name = "test-function"
    ctx.memory_limit_in_mb = 128
    ctx.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    ctx.aws_request_id = "test-request-id"
    return ctx


def test_get_item_found(handler_module: Any, mocker: Any) -> None:
    """GET /items/{id} returns 200 with item data when the item exists."""
    mock_repo = MagicMock()
    mock_repo.get_item.return_value = {"id": "abc", "name": "Widget"}
    mocker.patch("template.scenarios.api.handler.Repository", return_value=mock_repo)

    event = _apigw_event("GET", "/items/abc", path_params={"id": "abc"})
    response = handler_module.main(event, _lambda_context())

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["id"] == "abc"
    assert body["name"] == "Widget"
    mock_repo.get_item.assert_called_once_with("abc")


def test_post_item_created(handler_module: Any, mocker: Any) -> None:
    """POST /items returns 201 with the created item when the body is valid."""
    mock_repo = MagicMock()
    mock_repo.put_item.return_value = None
    mocker.patch("template.scenarios.api.handler.Repository", return_value=mock_repo)

    event = _apigw_event("POST", "/items", body={"id": "xyz", "name": "Gadget"})
    response = handler_module.main(event, _lambda_context())

    assert response["statusCode"] == 201
    body = json.loads(response["body"])
    assert body["id"] == "xyz"
    assert body["name"] == "Gadget"
    mock_repo.put_item.assert_called_once_with({"id": "xyz", "name": "Gadget"})


def test_get_item_not_found(handler_module: Any, mocker: Any) -> None:
    """GET /items/{id} returns 404 when the item does not exist."""
    mock_repo = MagicMock()
    mock_repo.get_item.return_value = None
    mocker.patch("template.scenarios.api.handler.Repository", return_value=mock_repo)

    event = _apigw_event("GET", "/items/missing", path_params={"id": "missing"})
    response = handler_module.main(event, _lambda_context())

    assert response["statusCode"] == 404


def test_post_item_invalid_body(handler_module: Any, mocker: Any) -> None:
    """POST /items returns 422 when the request body fails Pydantic validation."""
    mock_repo = MagicMock()
    mocker.patch("template.scenarios.api.handler.Repository", return_value=mock_repo)

    event = _apigw_event("POST", "/items", body={"id": "no-name"})
    response = handler_module.main(event, _lambda_context())

    assert response["statusCode"] == 422
    body = json.loads(response["body"])
    assert "errors" in body


def test_get_item_dynamodb_error(handler_module: Any, mocker: Any) -> None:
    """GET /items/{id} returns 500 when the repository raises an exception."""
    mock_repo = MagicMock()
    mock_repo.get_item.side_effect = Exception("DynamoDB unavailable")
    mocker.patch("template.scenarios.api.handler.Repository", return_value=mock_repo)

    event = _apigw_event("GET", "/items/boom", path_params={"id": "boom"})
    response = handler_module.main(event, _lambda_context())

    assert response["statusCode"] == 500


def test_post_item_dynamodb_error(handler_module: Any, mocker: Any) -> None:
    """POST /items returns 500 when the repository raises during put_item."""
    mock_repo = MagicMock()
    mock_repo.put_item.side_effect = Exception("DynamoDB unavailable")
    mocker.patch("template.scenarios.api.handler.Repository", return_value=mock_repo)

    event = _apigw_event("POST", "/items", body={"id": "err", "name": "Broken"})
    response = handler_module.main(event, _lambda_context())

    assert response["statusCode"] == 500
    body = json.loads(response["body"])
    assert "message" in body
