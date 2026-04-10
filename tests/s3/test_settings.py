from hypothesis import HealthCheck, given, settings
from hypothesis.strategies import just, one_of
from pydantic import ValidationError
from pytest import main, raises

from templates.s3.settings import Settings


def test_settings_defaults():
    _settings = Settings()  # type: ignore
    assert _settings.queue_url == "https://sqs.us-east-1.amazonaws.com/123456789012/test-queue"
    assert _settings.queue_region == "us-east-1"
    assert _settings.service_name == "s3-processor"
    assert _settings.metrics_namespace == "S3Processor"
    assert _settings.log_level == "INFO"


@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(queue_url=one_of(just(None), just("")))
def test_property_missing_sqs_queue_url_raises_validation_error(monkeypatch, queue_url):
    with monkeypatch.context() as m:
        if queue_url is None:
            m.delenv("QUEUE_URL", raising=False)
        else:
            m.setenv("QUEUE_URL", queue_url)
        with raises(ValidationError):
            Settings()  # type: ignore


if __name__ == "__main__":
    main()
