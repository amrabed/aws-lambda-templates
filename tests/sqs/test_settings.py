from pydantic import ValidationError
from pytest import raises

from templates.sqs.settings import Settings


def test_settings_valid(monkeypatch):
    monkeypatch.setenv("TABLE_NAME", "test-table")
    settings = Settings()  # type: ignore
    assert settings.table_name == "test-table"
    assert settings.service_name == "sqs-processor"


def test_settings_invalid(monkeypatch):
    monkeypatch.delenv("TABLE_NAME", raising=False)
    with raises(ValidationError):
        Settings()  # type: ignore
