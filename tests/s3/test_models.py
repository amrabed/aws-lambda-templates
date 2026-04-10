from hypothesis import given, settings
from hypothesis.strategies import builds
from pytest import main

from templates.s3.models import ProcessedMessage


@settings(max_examples=100, deadline=None)
@given(builds(ProcessedMessage))
def test_property_processed_message_serialization_round_trip(message):
    assert message == ProcessedMessage.model_validate_json(message.model_dump_json(by_alias=True))


if __name__ == "__main__":
    main()
