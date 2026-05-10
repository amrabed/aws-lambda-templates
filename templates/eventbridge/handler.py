from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.parameters import SecretsProvider
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.parser.models import EventBridgeModel
from aws_lambda_powertools.utilities.typing import LambdaContext
from requests import get

from templates.eventbridge.models import ApiResponse
from templates.eventbridge.settings import Settings
from templates.repository import Repository

settings = Settings()  # type: ignore
logger = Logger(service=settings.service_name)
tracer = Tracer(service=settings.service_name)
metrics = Metrics(namespace=settings.metrics_namespace, service=settings.service_name)
secrets_provider = SecretsProvider()
repository = Repository(settings.table_name)


class Handler:
    def __init__(self, secrets_provider: SecretsProvider, repository: Repository) -> None:
        self._secrets_provider = secrets_provider
        self._repository = repository

    @tracer.capture_method
    def handle(self, event: EventBridgeModel) -> ApiResponse:
        try:
            token = self._secrets_provider.get(settings.secret_name)
            response = get(
                settings.api_url,
                headers={"Authorization": f"Bearer {token}"},
                timeout=settings.api_timeout_seconds,
            )
            response.raise_for_status()
            # Bolt: Optimize by using Pydantic's Rust-based JSON parser directly on the raw bytes.
            # This avoids redundant dictionary creation and improves performance.
            api_response = ApiResponse.model_validate_json(response.content)
            self._repository.put_item(api_response.model_dump(by_alias=True, exclude_none=True))
            metrics.add_metric(name="ApiCallSuccess", unit=MetricUnit.Count, value=1)
            logger.info("API call succeeded", extra={"api_message": api_response.message})
            return api_response
        except Exception as exc:
            metrics.add_metric(name="ApiCallFailure", unit=MetricUnit.Count, value=1)
            logger.error("API call failed", exc_info=exc)
            raise


handler = Handler(secrets_provider=secrets_provider, repository=repository)


@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics
@event_parser(model=EventBridgeModel)
def main(event: EventBridgeModel, context: LambdaContext) -> None:
    handler.handle(event)
