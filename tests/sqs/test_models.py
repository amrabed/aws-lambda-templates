from templates.sqs.models import ProcessedItem, SqsMessage


def test_sqs_message_parsing():
    data = {"id": "123", "content": "hello"}
    message = SqsMessage.model_validate(data)
    assert message.id == "123"
    assert message.content == "hello"


def test_processed_item_model():
    item = ProcessedItem(id="123", content="hello", status="PROCESSED")
    assert item.id == "123"
    assert item.content == "hello"
    assert item.status == "PROCESSED"

    dump = item.model_dump(by_alias=True)
    assert dump["id"] == "123"
    assert dump["content"] == "hello"
    assert dump["status"] == "PROCESSED"
