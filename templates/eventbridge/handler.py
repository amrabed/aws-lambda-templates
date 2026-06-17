from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.parameters import SecretsProvider
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.parser.models import EventBridgeModel
from aws_lambda_powertools.utilities.typing import LambdaContext
from botocore.config import Config

from templates.eventbridge.models import ApiResponse
from templates.eventbridge.session import ApiSession
from templates.eventbridge.settings import Settings
from templates.repository import Repository

settings = Settings()  # type: ignore
logger = Logger(service=settings.service_name)
tracer = Tracer(service=settings.service_name)
metrics = Metrics(namespace=settings.metrics_namespace, service=settings.service_name)

boto_config = Config(
    tcp_keepalive=True, retries={"max_attempts": settings.secret_manager_max_retries, "mode": "standard"}
)
secrets_provider = SecretsProvider(boto_config=boto_config)
repository = Repository(settings.table_name, boto_config=boto_config)
session = ApiSession(
    max_retries=settings.api_max_retries,
    backoff_factor=settings.api_backoff_factor,
    timeout=settings.api_timeout_seconds,
)


class Handler:
    def __init__(self, secrets_provider: SecretsProvider, repository: Repository) -> None:
        self._secrets_provider = secrets_provider
        self._repository = repository

    @tracer.capture_method
    def handle(self, event: EventBridgeModel) -> ApiResponse:
        try:
            token = self._secrets_provider.get(settings.secret_name, max_age=settings.secret_cache_max_age)
            response = session.get(settings.api_url, headers={"Authorization": f"Bearer {token}"})
            response.raise_for_status()
            api_response = ApiResponse.model_validate_json(response.content)
            self._repository.put_item(api_response.dump())
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
