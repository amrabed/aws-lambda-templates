from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

from templates.${name}.settings import Settings

settings = Settings()

logger = Logger(service=settings.service_name)
tracer = Tracer(service=settings.service_name)
metrics = Metrics(namespace=settings.metrics_namespace)


@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics
def main(event: dict, context: LambdaContext) -> dict:
    """Lambda entry point.

    Args:
        event: The Lambda event.
        context: The Lambda execution context.

    Returns:
        The Lambda response.
    """
    logger.info("Hello from ${name}!")
    return {"message": "Hello from ${name}!"}
