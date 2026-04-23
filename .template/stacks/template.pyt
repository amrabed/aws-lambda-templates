from aws_cdk import Stack
from aws_cdk.aws_lambda import Code, Function, Runtime
from constructs import Construct


class ${camel_name}Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs: object) -> None:
        super().__init__(scope, construct_id, **kwargs)

        Function(
            self,
            "${camel_name}Function",
            runtime=Runtime.PYTHON_3_14,
            handler="templates.${name}.handler.main",
            code=Code.from_asset("."),
            environment={
                "SERVICE_NAME": "${name}",
                "METRICS_NAMESPACE": "${camel_name}",
            },
        )
