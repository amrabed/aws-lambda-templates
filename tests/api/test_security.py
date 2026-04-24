"""Security-focused unit tests for the REST API handler"""

from json import loads

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
def mock_repo(mocker) -> any:
    """Patch the module-level repository with a MagicMock."""
    mocker.patch("templates.repository.resource")
    import templates.api.handler as handler_module
    return mocker.patch.object(handler_module, "repository")

def _apigw_event(method: str, path: str, path_params: dict[str, str] | None = None) -> dict:
    return {
        "version": "1.0",
        "httpMethod": method,
        "path": path,
        "pathParameters": path_params or {},
        "headers": {"Content-Type": "application/json"},
        "requestContext": {
            "httpMethod": method,
            "path": path,
        },
    }

def test_get_item_strips_internal_fields(mock_repo, mocker):
    """GET /items/{id} should only return fields defined in the Item model."""
    import templates.api.handler as handler_module

    # Mock database record with an internal/sensitive field
    mock_repo.get_item.return_value = {
        "id": "abc",
        "name": "Widget",
        "internal_secret": "TOP_SECRET",
        "admin_note": "Do not show to user"
    }

    event = _apigw_event("GET", "/items/abc", path_params={"id": "abc"})
    response = handler_module.main(event, mocker.MagicMock())

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

def test_get_item_validation_error_returns_500(mock_repo, mocker):
    """GET /items/{id} returns 500 if the database record is invalid for the model."""
    import templates.api.handler as handler_module

    # Mock database record missing required 'name' field
    mock_repo.get_item.return_value = {"id": "abc"}

    event = _apigw_event("GET", "/items/abc", path_params={"id": "abc"})
    response = handler_module.main(event, mocker.MagicMock())

    assert response["statusCode"] == 500
    body = loads(response["body"])
    assert body["message"] == "Internal server error"

if __name__ == "__main__":
    main()
