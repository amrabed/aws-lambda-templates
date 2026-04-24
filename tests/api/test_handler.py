"""Unit tests for the REST API handler"""

from json import dumps, loads
from typing import Any

from pytest import fixture, main


@fixture(autouse=True)
def env(monkeypatch) -> None:
    """Set required environment variables for the handler module."""
    monkeypatch.setenv("TABLE_NAME", "test-table")
    monkeypatch.setenv("SERVICE_NAME", "test-service")
    monkeypatch.setenv("METRICS_NAMESPACE", "test-namespace")
    monkeypatch.setenv("POWERTOOLS_SERVICE_NAME", "test-service")
    monkeypatch.setenv("POWERTOOLS_METRICS_NAMESPACE", "test-namespace")
    monkeypatch.setenv("POWERTOOLS_METRICS_DISABLED", "true")
    monkeypatch.setenv("POWERTOOLS_TRACE_DISABLED", "true")


@fixture()
def mock_repo(mocker) -> Any:
    """Patch the module-level repository with a MagicMock."""
    mocker.patch("templates.repository.resource")
    import templates.api.handler as handler_module

    return mocker.patch.object(handler_module, "repository")


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
        "body": dumps(body) if body is not None else None,
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


def test_get_item_found(mock_repo: Any, lambda_context) -> None:
    """GET /items/{id} returns 200 with item data when the item exists."""
    import templates.api.handler as handler_module

    mock_repo.get_item.return_value = {"id": "abc", "name": "Widget"}

    event = _apigw_event("GET", "/items/abc", path_params={"id": "abc"})
    response = handler_module.main(event, lambda_context)

    assert response["statusCode"] == 200
    body = loads(response["body"])
    assert body["id"] == "abc"
    assert body["name"] == "Widget"
    mock_repo.get_item.assert_called_once_with("abc")


def test_post_item_created(mock_repo, lambda_context):
    """POST /items returns 201 with the created item when the body is valid."""
    import templates.api.handler as handler_module

    mock_repo.put_item.return_value = None

    event = _apigw_event("POST", "/items", body={"id": "xyz", "name": "Gadget"})
    response = handler_module.main(event, lambda_context)

    assert response["statusCode"] == 201
    body = loads(response["body"])
    assert body["id"] == "xyz"
    assert body["name"] == "Gadget"
    mock_repo.put_item.assert_called_once_with({"id": "xyz", "name": "Gadget"})


def test_get_item_not_found(mock_repo, lambda_context):
    """GET /items/{id} returns 404 when the item does not exist."""
    import templates.api.handler as handler_module

    mock_repo.get_item.return_value = None

    event = _apigw_event("GET", "/items/missing", path_params={"id": "missing"})
    response = handler_module.main(event, lambda_context)

    assert response["statusCode"] == 404


def test_post_item_invalid_body(mock_repo, lambda_context):
    """POST /items returns 422 when the request body fails Pydantic validation."""
    import templates.api.handler as handler_module

    event = _apigw_event("POST", "/items", body={"id": "no-name"})
    response = handler_module.main(event, lambda_context)

    assert response["statusCode"] == 422
    body = loads(response["body"])
    assert "errors" in body


def test_get_item_dynamodb_error(mock_repo, lambda_context):
    """GET /items/{id} returns 500 when the repository raises an exception."""
    import templates.api.handler as handler_module

    mock_repo.get_item.side_effect = Exception("DynamoDB unavailable")

    event = _apigw_event("GET", "/items/boom", path_params={"id": "boom"})
    response = handler_module.main(event, lambda_context)

    assert response["statusCode"] == 500


def test_post_item_dynamodb_error(mock_repo, lambda_context):
    """POST /items returns 500 when the repository raises during put_item."""
    import templates.api.handler as handler_module

    mock_repo.put_item.side_effect = Exception("DynamoDB unavailable")

    event = _apigw_event("POST", "/items", body={"id": "err", "name": "Broken"})
    response = handler_module.main(event, lambda_context)

    assert response["statusCode"] == 500
    body = loads(response["body"])
    assert "message" in body


def test_get_item_strips_internal_fields(mock_repo, lambda_context):
    """GET /items/{id} should only return fields defined in the Item model."""
    from templates.api.handler import main

    # Mock database record with an internal/sensitive field
    mock_repo.get_item.return_value = {
        "id": "abc",
        "name": "Widget",
        "internal_secret": "TOP_SECRET",
        "admin_note": "Do not show to user",
    }

    event = _apigw_event("GET", "/items/abc", path_params={"id": "abc"})
    response = main(event, lambda_context)

    assert response["statusCode"] == 200
    body = loads(response["body"])

    # Public fields should be present
    assert body["id"] == "abc"
    assert body["name"] == "Widget"

    # Sensitive/Internal fields should NOT be present
    assert "internal_secret" not in body
    assert "admin_note" not in body
    assert "internalSecret" not in body
    assert "adminNote" not in body


def test_get_item_validation_error_returns_500(mock_repo, lambda_context):
    """GET /items/{id} returns 500 if the database record is invalid for the model."""
    from templates.api.handler import main

    # Mock database record missing required 'name' field
    mock_repo.get_item.return_value = {"id": "abc"}

    event = _apigw_event("GET", "/items/abc", path_params={"id": "abc"})
    response = main(event, lambda_context)
    assert response["statusCode"] == 500
    body = loads(response["body"])
    assert body["message"] == "Internal server error"


if __name__ == "__main__":
    main()
