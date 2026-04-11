import sys
from unittest.mock import MagicMock

from pytest import fixture

# aws_xray_sdk is not installed in the test environment; stub it out before
# any handler module is imported so that Powertools Tracer initialises cleanly.
sys.modules.setdefault("aws_xray_sdk", MagicMock())
sys.modules.setdefault("aws_xray_sdk.core", MagicMock())


@fixture(autouse=True)
def aws_credentials(monkeypatch):
    """Mocked AWS Credentials for moto."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
