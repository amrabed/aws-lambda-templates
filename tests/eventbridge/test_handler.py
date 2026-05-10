"""Unit tests for the EventBridge API caller handler"""

import json

from pydantic import ValidationError
from pytest import fixture, main, raises
from requests import HTTPError


@fixture(autouse=True)
def env(monkeypatch) -> None:
    """Set required environment variables for the handler module."""
    monkeypatch.setenv("API_URL", "https://api.example.com/data")
    monkeypatch.setenv("SECRET_NAME", "test-secret")
    monkeypatch.setenv("SERVICE_NAME", "test-service")
    monkeypatch.setenv("METRICS_NAMESPACE", "test-namespace")
    monkeypatch.setenv("TABLE_NAME", "test-table")
    monkeypatch.setenv("POWERTOOLS_SERVICE_NAME", "test-service")
    monkeypatch.setenv("POWERTOOLS_METRICS_NAMESPACE", "test-namespace")
    monkeypatch.setenv("POWERTOOLS_METRICS_DISABLED", "true")
    monkeypatch.setenv("POWERTOOLS_TRACE_DISABLED", "true")


@fixture(autouse=True)
def stub_module_clients(mocker) -> None:
    """Stub AWS clients instantiated at module level so the handler can be imported."""
    mocker.patch("templates.repository.resource")


@fixture
def lambda_context(mocker):
    ctx = mocker.MagicMock()
    ctx.function_name = "test-function"
    ctx.memory_limit_in_mb = 128
    ctx.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    ctx.aws_request_id = "test-request-id"
    return ctx


def _valid_event() -> dict:
    return {
        "version": "0",
        "id": "abc-123",
        "source": "aws.events",
        "account": "123456789012",
        "time": "2024-01-01T00:00:00Z",
        "region": "us-east-1",
        "resources": [],
        "detail-type": "Scheduled Event",
        "detail": {},
    }


def _mock_response(mocker, json_data: dict, status_code: int = 200):
    mock_resp = mocker.MagicMock()
    mock_resp.json.return_value = json_data
    mock_resp.content = json.dumps(json_data).encode()
    mock_resp.status_code = status_code
    mock_resp.raise_for_status.return_value = None
    return mock_resp


def test_successful_invocation(mocker, lambda_context) -> None:
    """Token loaded, API called, ApiCallSuccess metric emitted, repository.put_item called."""
    import templates.eventbridge.handler as handler_module

    mock_secrets = mocker.patch.object(handler_module, "secrets_provider")
    mock_get = mocker.patch.object(handler_module, "get")
    mock_repo = mocker.patch.object(handler_module, "repository")
    mock_metrics = mocker.patch.object(handler_module, "metrics")

    handler_module.handler._secrets_provider = mock_secrets
    handler_module.handler._repository = mock_repo

    mock_secrets.get.return_value = "my-token"
    mock_get.return_value = _mock_response(mocker, {"id": "abc-123", "message": "ok"})

    handler_module.main(_valid_event(), lambda_context)

    mock_secrets.get.assert_called_once()
    mock_get.assert_called_once_with(
        mocker.ANY,
        headers={"Authorization": "Bearer my-token"},
        timeout=10,
    )
    mock_repo.put_item.assert_called_once_with({"id": "abc-123", "message": "ok"})
    mock_metrics.add_metric.assert_called_with(name="ApiCallSuccess", unit=mocker.ANY, value=1)


def test_secret_loading_failure(mocker, lambda_context) -> None:
    """SecretsProvider.get raises -> handler re-raises, ApiCallFailure emitted."""
    import templates.eventbridge.handler as handler_module

    mock_secrets = mocker.patch.object(handler_module, "secrets_provider")
    mocker.patch.object(handler_module, "get")
    mock_repo = mocker.patch.object(handler_module, "repository")
    mock_metrics = mocker.patch.object(handler_module, "metrics")

    handler_module.handler._secrets_provider = mock_secrets
    handler_module.handler._repository = mock_repo

    mock_secrets.get.side_effect = Exception("Secrets Manager unavailable")

    with raises(Exception, match="Secrets Manager unavailable"):
        handler_module.main(_valid_event(), lambda_context)

    mock_metrics.add_metric.assert_called_with(name="ApiCallFailure", unit=mocker.ANY, value=1)


def test_api_non_2xx_response(mocker, lambda_context) -> None:
    """requests.get raises HTTPError on non-2xx -> handler re-raises, ApiCallFailure emitted."""
    import templates.eventbridge.handler as handler_module

    mock_secrets = mocker.patch.object(handler_module, "secrets_provider")
    mock_get = mocker.patch.object(handler_module, "get")
    mock_repo = mocker.patch.object(handler_module, "repository")
    mock_metrics = mocker.patch.object(handler_module, "metrics")

    handler_module.handler._secrets_provider = mock_secrets
    handler_module.handler._repository = mock_repo

    mock_secrets.get.return_value = "my-token"
    mock_resp = mocker.MagicMock()
    mock_resp.raise_for_status.side_effect = HTTPError(response=mocker.MagicMock(status_code=500))
    mock_get.return_value = mock_resp

    with raises(HTTPError):
        handler_module.main(_valid_event(), lambda_context)

    mock_metrics.add_metric.assert_called_with(name="ApiCallFailure", unit=mocker.ANY, value=1)


def test_api_network_exception(mocker, lambda_context) -> None:
    """requests.get raises ConnectionError -> handler re-raises, ApiCallFailure emitted."""
    import templates.eventbridge.handler as handler_module

    mock_secrets = mocker.patch.object(handler_module, "secrets_provider")
    mock_get = mocker.patch.object(handler_module, "get")
    mock_repo = mocker.patch.object(handler_module, "repository")
    mock_metrics = mocker.patch.object(handler_module, "metrics")

    handler_module.handler._secrets_provider = mock_secrets
    handler_module.handler._repository = mock_repo

    mock_secrets.get.return_value = "my-token"
    mock_get.side_effect = ConnectionError("Connection refused")

    with raises(ConnectionError):
        handler_module.main(_valid_event(), lambda_context)

    mock_metrics.add_metric.assert_called_with(name="ApiCallFailure", unit=mocker.ANY, value=1)


def test_invalid_eventbridge_event(mocker, lambda_context) -> None:
    """Missing required fields -> @event_parser raises ValidationError before handler is called."""
    import templates.eventbridge.handler as handler_module

    mock_secrets = mocker.patch.object(handler_module, "secrets_provider")
    mock_get = mocker.patch.object(handler_module, "get")
    mock_repo = mocker.patch.object(handler_module, "repository")

    handler_module.handler._secrets_provider = mock_secrets
    handler_module.handler._repository = mock_repo

    invalid_event = {"source": "aws.events", "detail-type": "Scheduled Event"}

    with raises(ValidationError):
        handler_module.main(invalid_event, lambda_context)

    mock_get.assert_not_called()


def test_dynamodb_write_failure(mocker, lambda_context) -> None:
    """repository.put_item raises -> handler re-raises, ApiCallFailure emitted."""
    import templates.eventbridge.handler as handler_module

    mock_secrets = mocker.patch.object(handler_module, "secrets_provider")
    mock_get = mocker.patch.object(handler_module, "get")
    mock_repo = mocker.patch.object(handler_module, "repository")
    mock_metrics = mocker.patch.object(handler_module, "metrics")

    handler_module.handler._secrets_provider = mock_secrets
    handler_module.handler._repository = mock_repo

    mock_secrets.get.return_value = "my-token"
    mock_get.return_value = _mock_response(mocker, {"id": "abc-123", "message": "ok"})
    mock_repo.put_item.side_effect = Exception("DynamoDB unavailable")

    with raises(Exception, match="DynamoDB unavailable"):
        handler_module.main(_valid_event(), lambda_context)

    mock_metrics.add_metric.assert_called_with(name="ApiCallFailure", unit=mocker.ANY, value=1)


if __name__ == "__main__":
    main()
