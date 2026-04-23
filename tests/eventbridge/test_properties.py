"""Property-based tests for the EventBridge API caller."""

import sys
from unittest.mock import MagicMock, patch

from hypothesis import HealthCheck, given
from hypothesis import settings as h_settings
from hypothesis import strategies as st
from pytest import fixture, main, raises
from requests import HTTPError

# Patch SecretsProvider globally so that handler.py can be imported without
# real AWS credentials. Individual tests override the instance via patch.object.
patch("aws_lambda_powertools.utilities.parameters.SecretsProvider", MagicMock()).start()

# Clear any previously cached (broken) handler modules so they re-import cleanly.
# This runs at conftest import time, before any test collection or execution.
for _mod in list(sys.modules):
    if _mod.startswith("templates.eventbridge"):
        sys.modules.pop(_mod, None)


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


# Feature: eventbridge-api-caller, Property 1: Handler accepts any valid EventBridge event shape
@given(
    source=st.text(),
    detail_type=st.text(),
    detail=st.dictionaries(st.text(), st.text()),
)
@h_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_valid_event_shapes(mocker, source, detail_type, detail) -> None:
    import templates.eventbridge.handler as handler_module

    mock_secrets = mocker.patch.object(handler_module, "secrets_provider")
    mock_get = mocker.patch.object(handler_module, "get")
    mock_provider = mocker.patch.object(handler_module, "provider")

    handler_module.handler._secrets_provider = mock_secrets
    handler_module.handler._provider = mock_provider

    mock_secrets.get.return_value = "test-token"
    mock_resp = mocker.MagicMock()
    mock_resp.json.return_value = {"id": "test-id", "message": "ok"}
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    from aws_lambda_powertools.utilities.parser.models import EventBridgeModel

    event_dict = {
        "version": "0",
        "id": "abc-123",
        "source": source,
        "account": "123456789012",
        "time": "2024-01-01T00:00:00Z",
        "region": "us-east-1",
        "resources": [],
        "detail-type": detail_type,
        "detail": detail,
    }
    eb_event = EventBridgeModel.model_validate(event_dict)
    assert eb_event is not None

    mock_context = mocker.MagicMock()
    mock_context.function_name = "test-function"
    mock_context.memory_limit_in_mb = 128
    mock_context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    mock_context.aws_request_id = "test-request-id"

    handler_module.main(event_dict, mock_context)
    mock_get.assert_called_once()
    mock_get.reset_mock()
    mock_secrets.get.reset_mock()
    mock_provider.table.put_item.reset_mock()


# Feature: eventbridge-api-caller, Property 2: Invalid event prevents ApiClient call
@given(missing_key=st.sampled_from(["source", "detail-type", "detail"]))
@h_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_invalid_event_prevents_api_call(mocker, missing_key) -> None:
    from pydantic import ValidationError

    import templates.eventbridge.handler as handler_module

    mock_secrets = mocker.patch.object(handler_module, "secrets_provider")
    mock_get = mocker.patch.object(handler_module, "get")
    mock_provider = mocker.patch.object(handler_module, "provider")

    handler_module.handler._secrets_provider = mock_secrets
    handler_module.handler._provider = mock_provider

    valid_event = {
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
    invalid_event = {k: v for k, v in valid_event.items() if k != missing_key}

    mock_context = mocker.MagicMock()
    mock_context.function_name = "test-function"
    mock_context.memory_limit_in_mb = 128
    mock_context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    mock_context.aws_request_id = "test-request-id"

    with raises(ValidationError):
        handler_module.main(invalid_event, mock_context)
    mock_get.assert_not_called()
    mock_get.reset_mock()


# Feature: eventbridge-api-caller, Property 3: SecretClient exception propagates
@given(exc=st.from_type(Exception))
@h_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_secret_exception_propagates(mocker, exc) -> None:
    import templates.eventbridge.handler as handler_module

    mock_secrets = mocker.patch.object(handler_module, "secrets_provider")
    mock_get = mocker.patch.object(handler_module, "get")
    mock_provider = mocker.patch.object(handler_module, "provider")

    handler_module.handler._secrets_provider = mock_secrets
    handler_module.handler._provider = mock_provider

    mock_secrets.get.side_effect = exc

    mock_context = mocker.MagicMock()
    mock_context.function_name = "test-function"
    mock_context.memory_limit_in_mb = 128
    mock_context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    mock_context.aws_request_id = "test-request-id"

    valid_event = {
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

    with raises(Exception):
        handler_module.main(valid_event, mock_context)

    mock_secrets.get.side_effect = None
    mock_get.reset_mock()


# Feature: eventbridge-api-caller, Property 4: Bearer token header for any token string
@given(token=st.text(min_size=1))
@h_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_bearer_token_header(mocker, token) -> None:
    import templates.eventbridge.handler as handler_module

    mock_secrets = mocker.patch.object(handler_module, "secrets_provider")
    mock_get = mocker.patch.object(handler_module, "get")
    mock_provider = mocker.patch.object(handler_module, "provider")

    handler_module.handler._secrets_provider = mock_secrets
    handler_module.handler._provider = mock_provider

    mock_secrets.get.return_value = token
    mock_resp = mocker.MagicMock()
    mock_resp.json.return_value = {"id": "test-id", "message": "ok"}
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    mock_context = mocker.MagicMock()
    mock_context.function_name = "test-function"
    mock_context.memory_limit_in_mb = 128
    mock_context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    mock_context.aws_request_id = "test-request-id"

    valid_event = {
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
    handler_module.main(valid_event, mock_context)

    mock_get.assert_called_once_with(mocker.ANY, headers={"Authorization": f"Bearer {token}"})
    mock_get.reset_mock()
    mock_secrets.get.reset_mock()


# Feature: eventbridge-api-caller, Property 5: 2xx response parsed into ApiResponse
@given(
    status_code=st.integers(200, 299),
    message=st.text(min_size=1),
)
@h_settings(max_examples=100)
def test_2xx_response_parsed(status_code, message) -> None:
    from templates.eventbridge.models import ApiResponse

    response = ApiResponse.model_validate({"id": "test-id", "message": message})
    assert response.message == message


# Feature: eventbridge-api-caller, Property 6: ApiClient failure propagates exception
@given(status_code=st.integers(400, 599))
@h_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_api_failure_propagates(mocker, status_code) -> None:
    import templates.eventbridge.handler as handler_module

    mock_secrets = mocker.patch.object(handler_module, "secrets_provider")
    mock_get = mocker.patch.object(handler_module, "get")
    mock_provider = mocker.patch.object(handler_module, "provider")

    handler_module.handler._secrets_provider = mock_secrets
    handler_module.handler._provider = mock_provider

    mock_secrets.get.return_value = "test-token"
    mock_resp = mocker.MagicMock()
    mock_resp.raise_for_status.side_effect = HTTPError(response=mocker.MagicMock(status_code=status_code))
    mock_get.return_value = mock_resp

    mock_context = mocker.MagicMock()
    mock_context.function_name = "test-function"
    mock_context.memory_limit_in_mb = 128
    mock_context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    mock_context.aws_request_id = "test-request-id"

    valid_event = {
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

    with raises(Exception):
        handler_module.main(valid_event, mock_context)

    mock_get.reset_mock()
    mock_secrets.get.reset_mock()


# Feature: eventbridge-api-caller, Property 7: Missing required env var raises ValidationError
@given(var_name=st.sampled_from(["API_URL", "SECRET_NAME", "SERVICE_NAME", "METRICS_NAMESPACE", "TABLE_NAME"]))
@h_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_missing_env_var_raises(monkeypatch, var_name) -> None:
    from pydantic import ValidationError

    monkeypatch.delenv(var_name, raising=False)

    # Reload settings module to pick up the changed env
    if "templates.eventbridge.settings" in sys.modules:
        del sys.modules["templates.eventbridge.settings"]

    from templates.eventbridge.settings import Settings

    with raises(ValidationError):
        Settings()

    # Restore the env var for subsequent examples
    env_defaults = {
        "API_URL": "https://api.example.com/data",
        "SECRET_NAME": "test-secret",
        "SERVICE_NAME": "test-service",
        "METRICS_NAMESPACE": "test-namespace",
        "TABLE_NAME": "test-table",
    }
    monkeypatch.setenv(var_name, env_defaults[var_name])


# Feature: eventbridge-api-caller, Property 8: EventBridgeModel parses any valid source and detail-type
@given(
    source=st.text(),
    detail_type=st.text(),
    detail=st.dictionaries(st.text(), st.text()),
)
@h_settings(max_examples=100)
def test_eventbridge_event_round_trip(source, detail_type, detail) -> None:
    from aws_lambda_powertools.utilities.parser.models import EventBridgeModel

    input_dict = {
        "version": "0",
        "id": "abc-123",
        "source": source,
        "account": "123456789012",
        "time": "2024-01-01T00:00:00Z",
        "region": "us-east-1",
        "resources": [],
        "detail-type": detail_type,
        "detail": detail,
    }
    event = EventBridgeModel.model_validate(input_dict)
    assert event.source == source
    assert event.detail_type == detail_type
    assert event.detail == detail


# Feature: eventbridge-api-caller, Property 9: ApiResponse camelCase round-trip
@given(message=st.text(min_size=1))
@h_settings(max_examples=100)
def test_api_response_round_trip(message) -> None:
    from templates.eventbridge.models import ApiResponse

    input_dict = {"id": "test-id", "message": message}
    response = ApiResponse.model_validate(input_dict)
    output = response.model_dump(by_alias=True)
    assert output == input_dict


# Feature: eventbridge-api-caller, Property 10: Successful API response is persisted to DynamoDB
@given(status=st.text(min_size=1))
@h_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_successful_response_persisted(mocker, status) -> None:
    import templates.eventbridge.handler as handler_module

    mock_secrets = mocker.patch.object(handler_module, "secrets_provider")
    mock_get = mocker.patch.object(handler_module, "get")
    mock_provider = mocker.patch.object(handler_module, "provider")

    handler_module.handler._secrets_provider = mock_secrets
    handler_module.handler._provider = mock_provider

    mock_secrets.get.return_value = "test-token"
    mock_resp = mocker.MagicMock()
    mock_resp.json.return_value = {"id": "test-id", "message": status}
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    mock_context = mocker.MagicMock()
    mock_context.function_name = "test-function"
    mock_context.memory_limit_in_mb = 128
    mock_context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    mock_context.aws_request_id = "test-request-id"

    valid_event = {
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
    handler_module.main(valid_event, mock_context)

    mock_provider.table.put_item.assert_called_once_with(Item={"id": "test-id", "message": status})
    mock_provider.table.put_item.reset_mock()
    mock_get.reset_mock()
    mock_secrets.get.reset_mock()


# Feature: eventbridge-api-caller, Property 11: DynamoDB write failure propagates exception
@given(exc=st.from_type(Exception))
@h_settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_dynamodb_write_failure_propagates(mocker, exc) -> None:
    import templates.eventbridge.handler as handler_module

    mock_secrets = mocker.patch.object(handler_module, "secrets_provider")
    mock_get = mocker.patch.object(handler_module, "get")
    mock_provider = mocker.patch.object(handler_module, "provider")

    handler_module.handler._secrets_provider = mock_secrets
    handler_module.handler._provider = mock_provider

    mock_secrets.get.return_value = "test-token"
    mock_resp = mocker.MagicMock()
    mock_resp.json.return_value = {"id": "test-id", "message": "ok"}
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp
    mock_provider.table.put_item.side_effect = exc

    mock_context = mocker.MagicMock()
    mock_context.function_name = "test-function"
    mock_context.memory_limit_in_mb = 128
    mock_context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    mock_context.aws_request_id = "test-request-id"

    valid_event = {
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

    with raises(Exception):
        handler_module.main(valid_event, mock_context)

    mock_provider.table.put_item.side_effect = None
    mock_get.reset_mock()
    mock_secrets.get.reset_mock()
    mock_provider.table.put_item.reset_mock()


if __name__ == "__main__":
    main()
