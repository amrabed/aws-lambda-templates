from pytest import fixture


@fixture
def lambda_context(mocker):
    context = mocker.MagicMock()
    context.function_name = "test-function"
    return context


def test_handler(lambda_context):
    from templates.${name}.handler import main

    event = {}
    response = main(event, lambda_context)
    assert response["message"] == "Hello from ${name}!"


if __name__ == "__main__":
    from pytest import main

    main()
