import os
import re
import sys


def to_camel_case(snake_str):
    components = snake_str.split("_")
    return "".join(x.title() for x in components)


def to_title_case(snake_str):
    components = snake_str.split("_")
    return " ".join(x.title() for x in components)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/new_template.py <name>")
        sys.exit(1)

    name = sys.argv[1].lower().replace("-", "_")
    camel_name = to_camel_case(name)
    title_name = to_title_case(name)

    # 1. Create directories
    os.makedirs(f"templates/{name}", exist_ok=True)
    os.makedirs(f"tests/{name}", exist_ok=True)

    # 2. Generate skeleton files

    # templates/<name>/__init__.py
    with open(f"templates/{name}/__init__.py", "w") as f:
        pass

    # templates/<name>/models.py
    with open(f"templates/{name}/models.py", "w") as f:
        f.write("from pydantic import BaseModel\n\n\nclass Item(BaseModel):\n    id: str\n    name: str\n")

    # templates/<name>/settings.py
    with open(f"templates/{name}/settings.py", "w") as f:
        f.write(f"""from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = Field(description="Powertools service name", default="{name}")
    metrics_namespace: str = Field(description="Powertools metrics namespace", default="{camel_name}")
""")

    # templates/<name>/handler.py
    with open(f"templates/{name}/handler.py", "w") as f:
        f.write(f"""from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

from templates.{name}.settings import Settings

settings = Settings()

logger = Logger(service=settings.service_name)
tracer = Tracer(service=settings.service_name)
metrics = Metrics(namespace=settings.metrics_namespace)


@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics
def main(event: dict, context: LambdaContext) -> dict:
    \"\"\"Lambda entry point.

    Args:
        event: The Lambda event.
        context: The Lambda execution context.

    Returns:
        The Lambda response.
    \"\"\"
    logger.info("Hello from {name}!")
    return {{"message": "Hello from {name}!"}}
""")

    # tests/<name>/__init__.py
    with open(f"tests/{name}/__init__.py", "w") as f:
        pass

    # tests/<name>/test_handler.py
    with open(f"tests/{name}/test_handler.py", "w") as f:
        f.write(f"""from pytest import fixture
from templates.{name}.handler import main

@fixture
def lambda_context(mocker):
    ctx = mocker.MagicMock()
    ctx.function_name = "test-function"
    return ctx

def test_handler(lambda_context):
    event = {{}}
    response = main(event, lambda_context)
    assert response["message"] == "Hello from {name}!"
""")

    # infra/stacks/<name>.py
    with open(f"infra/stacks/{name}.py", "w") as f:
        f.write(f"""from aws_cdk import Stack
from aws_cdk.aws_lambda import Code, Function, Runtime
from constructs import Construct


class {camel_name}Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs: object) -> None:
        super().__init__(scope, construct_id, **kwargs)

        Function(
            self,
            "{camel_name}Function",
            runtime=Runtime.PYTHON_3_13,
            handler="templates.{name}.handler.main",
            code=Code.from_asset("."),
            environment={{
                "SERVICE_NAME": "{name}",
                "METRICS_NAMESPACE": "{camel_name}",
            }},
        )
""")

    # docs/reference/<name>.md
    with open(f"docs/reference/{name}.md", "w") as f:
        f.write(f"# {title_name}\n::: templates.{name}.handler\n")

    # docs/template/<name>.md
    with open(f"docs/template/{name}.md", "w") as f:
        f.write(f"""# {title_name}
Template description for {title_name}.

## Architecture

1.  **AWS Lambda function**: Handles events.

## Code

- **Function code**: [`templates/{name}`](/templates/{name})
- **Unit tests**: [`tests/{name}`](/tests/{name})
- **Infra stack**: [`infra/stacks/{name}.py`](/infra/stacks/{name}.py)

## Deployment

Deploy the stack using:

```bash
make deploy STACK={name}
```
""")

    # 3. Update Registry Files

    # infra/app.py
    with open("infra/app.py", "r") as f:
        content = f.read()

    import_line = f"from infra.stacks.{name} import {camel_name}Stack"
    if import_line not in content:
        # Find the last stack import
        lines = content.splitlines()
        last_import_idx = -1
        for i, line in enumerate(lines):
            if "from infra.stacks." in line:
                last_import_idx = i

        lines.insert(last_import_idx + 1, import_line)

        # Update STACK_REGISTRY
        content = "\n".join(lines)
        registry_match = re.search(r"STACK_REGISTRY: dict\[str, type\] = \{(.*?)\}", content, re.DOTALL)
        if registry_match:
            registry_content = registry_match.group(1)
            new_registry_entry = f'    "{name}": {camel_name}Stack,'
            if f'"{name}":' not in registry_content:
                updated_registry = registry_content.rstrip() + "\n" + new_registry_entry + "\n"
                content = content.replace(registry_content, updated_registry)

        with open("infra/app.py", "w") as f:
            f.write(content)

    # .github/workflows/deploy.yml
    with open(".github/workflows/deploy.yml", "r") as f:
        content = f.read()

    if f"- {name}" not in content:
        # Update options
        options_match = re.search(r"options:\n(.*?)(?=\n\w+:|$)", content, re.DOTALL)
        if options_match:
            options_content = options_match.group(1)
            if f"- {name}" not in options_content:
                updated_options = options_content.rstrip() + f"\n          - {name}\n"
                content = content.replace(options_content, updated_options)

        # Update matrix
        matrix_match = re.search(r"matrix:\n\s+stack: \[(.*?)\]", content)
        if matrix_match:
            matrix_content = matrix_match.group(1)
            if name not in matrix_content:
                updated_matrix = matrix_content + f", {name}"
                content = content.replace(f"stack: [{matrix_content}]", f"stack: [{updated_matrix}]")

        with open(".github/workflows/deploy.yml", "w") as f:
            f.write(content)

    # mkdocs.yml
    with open("mkdocs.yml", "r") as f:
        content = f.read()

    if f"{name}.md" not in content:
        # Add to Templates
        templates_match = re.search(r"Templates:\n(.*?)(?=\n  - Reference:|$)", content, re.DOTALL)
        if templates_match:
            templates_content = templates_match.group(1)
            new_nav_entry = f"    - {title_name}: template/{name}.md"
            if new_nav_entry not in templates_content:
                updated_templates = templates_content.rstrip() + "\n" + new_nav_entry + "\n"
                content = content.replace(templates_content, updated_templates)

        # Add to Reference
        reference_match = re.search(r"Reference:\n(.*?)(?=\nplugins:|$)", content, re.DOTALL)
        if reference_match:
            reference_content = reference_match.group(1)
            new_ref_entry = f"    - {title_name}: reference/{name}.md"
            if new_ref_entry not in reference_content:
                updated_reference = reference_content.rstrip() + "\n" + new_ref_entry + "\n"
                content = content.replace(reference_content, updated_reference)

        with open("mkdocs.yml", "w") as f:
            f.write(content)

    # Makefile
    with open("Makefile", "r") as f:
        content = f.read()

    stack_map_line = f"STACK_MAP_{name} " + " " * (25 - len(name)) + f"= {camel_name}Stack"
    if stack_map_line not in content:
        # Find the last STACK_MAP entry
        lines = content.splitlines()
        last_map_idx = -1
        for i, line in enumerate(lines):
            if "STACK_MAP_" in line:
                last_map_idx = i

        if last_map_idx != -1:
            lines.insert(last_map_idx + 1, stack_map_line)

            # Update deploy/destroy messages
            for i, line in enumerate(lines):
                if "Usage: make deploy STACK=" in line:
                    if f"|{name}" not in line:
                        lines[i] = line.replace(">", f"|{name}>")
                if "Usage: make destroy STACK=" in line:
                    if f"|{name}" not in line:
                        lines[i] = line.replace(">", f"|{name}>")

            with open("Makefile", "w") as f:
                f.write("\n".join(lines) + "\n")

    print(f"Successfully created template '{name}'")


if __name__ == "__main__":
    main()
