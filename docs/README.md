# AWS Lambda Templates - Python
[![Python](https://img.shields.io/badge/python-3.14+-3776AB.svg?logo=python&style=flat-square)](https://python.org)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-D7FF64.svg?logo=ruff&style=flat-square)](https://docs.astral.sh/ruff)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](LICENSE.md)

Production-ready plug-and-play **AWS Lambda templates in Python** for different real-life scenarios.

The templates apply best practices by using [AWS Lambda Powertools](https://docs.aws.amazon.com/powertools/python) for:

- CloudWatch Logs and Metrics
- X-ray Tracing
- Batch Processing
- Event Handling
- Parameter/Secret Loading

## Templates

- [Bedrock Agent](template/agent.md): Handle Bedrock Agent function-based actions
- [GraphQL API](template/graphql.md): Handle AppSync GraphQL requests
- [REST API](template/api.md): Handle REST API requests
- [DynamoDB Stream](template/stream.md): Batch process stream events
- [EventBridge](template/eventbridge.md): Call external API on event
- [S3 to SQS](template/s3.md): Send messages to queue on S3 object changes
- [SQS to DynamoDB](template/sqs.md): Batch Process SQS messages

## Features

Templates come pre-wired with:

- **AWS Lambda Best Practices**: Integrated [AWS Lambda Powertools](https://docs.aws.amazon.com/powertools/python)
- **Clean Architecture**: Separation of concerns using the Repository pattern for data access
- **Data Modeling**: Strong typing and validation using [Pydantic](https://docs.pydantic.dev)
- **Infrastructure as Code**: [AWS CDK](https://aws.amazon.com/cdk) stacks
- **Testing**: Comprehensive [pytest](https://pytest.org) suite with [moto](http://docs.getmoto.org) for AWS mocking and [hypothesis](https://hypothesis.readthedocs.io) for property-based testing
- **Code Quality**: [ruff](https://docs.astral.sh/ruff) for linting and formatting, [pyright](https://microsoft.github.io/pyright) for type checking, and test coverage using [coverage](https://coverage.readthedocs.io)
- **Dependency Control**: [uv](https://docs.astral.sh/uv/) for dependency management and [Dependabot](https://docs.github.com/en/code-security/dependabot) for automated dependency updates
- **Documentation**: Automatic documentation using [MkDocs](https://www.mkdocs.org) and [mkdocstrings](https://mkdocstrings.github.io)
- **Development environment**: [Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers) for dockerized development environment
- **Pre-commit Validations**: [pre-commit](https://pre-commit.com) hooks
- **Workflow Automation**: [GitHub Actions](https://github.com/features/actions) for CI/CD and documentation auto-deployment to [GitHub Pages](https://pages.github.com)

### GitHub files
The repository also comes preloaded with these GitHub files:

- AI Agent guidelines
- Pull request template
- Issue templates
    + Bug report
    + Feature request
    + Question
- Contributing guidelines
- Funding file
- Code owners
- MIT License

## How to use
Click this button to create a new repository for your project, then clone the new repository. Enjoy!

[![Use this template](https://img.shields.io/badge/Use%20this%20template-238636?style=for-the-badge)](https://github.com/amrabed/aws-lambda-templates/generate)

### Rename the project
Run `make project` once after cloning, before any other setup steps:

```bash
make project NAME="my-project" DESCRIPTION="My project description" AUTHOR="Jane Doe" EMAIL="jane" GITHUB="janedoe"
```

Pass the following parameters:

Parameter | Description
--- | ---
`NAME` | Project new name
`DESCRIPTION` | Project short description
`AUTHOR` | Author name
`EMAIL` | Author email
`GITHUB` | GitHub username (for GitHub funding)
`SOURCE` | (optional) Source folder name

## Prerequisites

### Dev container
- Docker

### Local environment
- Python 3.14+
- uv
- Docker (for Dev Containers)
- AWS CDK CLI (for deployment)

## Setup

### Install dependencies
To install the project dependencies defined in `pyproject.toml`, run:
```bash
make install
```

### Install pre-commit hooks
To install the pre-commit hooks for the project to format and lint your code automatically before committing, run:
```bash
make precommit
```

### Activate virtual environment
To activate the virtual environment, run:
```bash
make venv
```

### Format and lint code
To format and lint project code, run:
```bash
make lint
```

### Run tests with coverage
To run all tests (including Hypothesis property-based tests) and show the coverage report, run:
```bash
make test
```

`make test` runs both standard pytest tests and Hypothesis property-based tests in a single command.

### Build a new template

To start building a new Lambda template, use:

```bash
make new template=<name>
```

Or, equivalently:

```bash
uv run new --name <name>
```

This runs the `new` uv script, which builds a skeleton for the new template from `.template`.


### Deploy a stack
Infrastructure is defined as AWS CDK stacks under [`infra/stacks/`](/infra/stacks). 
The CDK entry point is [`infra/app.py`](/infra/app.py). 
The `STACK` environment variable selects which stack to synthesise.

```bash
make deploy STACK=<stack-key>
```

Pass `AWS_PROFILE` to use a named AWS CLI profile:
```bash
make deploy STACK=<stack-key> AWS_PROFILE=<my-profile>
```

### Destroy a stack
```bash
make destroy STACK=<stack-key>
```

### Generating documentation

To build and publish the project documentation to GitHub Pages, run:
```bash
make docs
```

That pushes the new documentation to the `gh-pages` branch. Make sure GitHub Pages is enabled in your repository settings and using the `gh-pages` branch for the documentation to be publicly available.

### Local preview
To serve the documentation on a local server, run:
```bash
make local
```

## Coding Conventions

- **camelCase for JSON**: All models use `alias_generator=to_camel` so that JSON payloads use camelCase while Python attributes use snake_case.
- **Environment Variables**: Managed via `BaseSettings` in `settings.py` files.
- **Documentation**: Every field in a Pydantic model must include a `Field(description="...")`.
- **Repository Pattern**: All database calls are encapsulated in a `Repository` class for better testability.


## Project Structure

```
├── .devcontainer                   # Dev container folder
│   ├── devcontainer.json           # Dev container configuration
│   └── Dockerfile                  # Dev container Dockerfile
├── .github                         # GitHub folder
│   ├── dependabot.yaml             # Dependabot configuration
│   ├── CODEOWNERS                  # Code owners
│   ├── FUNDING.yml                 # GitHub funding
│   ├── PULL_REQUEST_TEMPLATE.md    # Pull request template
│   ├── ISSUE_TEMPLATE              # Issue templates
│   │   ├── bug.md                  # Bug report template
│   │   ├── feature.md              # Feature request template
│   │   └── question.md             # Question template
│   └── workflows                   # GitHub Actions workflows
│       ├── check.yml               # Workflow to validate code on push
│       ├── deploy.yml              # Workflow to deploy infra and code
│       └── docs.yml                # Workflow to publish documentation
├── .gitignore                      # Git-ignored file list
├── .pre-commit-config.yaml         # Pre-commit configuration file
├── .vscode                         # VS Code folder
├── Makefile                        # Make commands
├── pyproject.toml                  # Configuration file for different tools
├── mkdocs.yml                      # MkDocs configuration file
├── docs                            # Documentation folder
│   ├── README.md                   # Read-me file & documentation home page
│   ├── CONTRIBUTING.md             # Contributing guidelines
│   ├── LICENSE.md                  # Project license
│   ├── template                    # Templates summary page
│   │   ├── agent.md                # Bedrock agent documentation page
│   │   ├── api.md                  # API documentation page
│   │   ├── eventbridge.md          # EventBridge documentation page
│   │   ├── graphql.md              # AppSync GRAPHQL documentation page
│   │   ├── s3.md                   # S3 documentation page
│   │   ├── stream.md               # Stream documentation page
│   │   └── sqs.md                  # SQS documentation page
│   └── reference                   # Reference section
│       ├── repository.md           # Repository reference page
│       ├── agent.md                # Bedrock agent reference page
│       ├── api.md                  # API scenario reference page
│       ├── eventbridge.md          # EventBridge scenario reference page
│       ├── graphql.md              # AppSync GraphQL scenario reference page
│       ├── s3.md                   # S3 scenario reference page
│       ├── stream.md               # Stream scenario reference page
│       └── sqs.md                  # SQS scenario reference page
├── templates                       # Main package
│   ├── agent                       # Bedrock agent function handler
│   ├── api                         # API request handler
│   ├── eventbridge                 # EventBridge event handler
│   ├── graphql                     # AppSync GraphQL resolver
│   ├── s3                          # S3 event handler
│   ├── stream                      # DynamoDB stream batch processor
│   ├── sqs                         # SQS message handler
│   ├── queue.py                    # SQS queue interaction
│   └── repository.py               # DynamoDB repository
├── infra                           # AWS CDK infrastructure
│   ├── app.py                      # CDK entry point
│   └── stacks                      # CDK stack definitions
│       ├── agent.py                # Bedrock agent stack
│       ├── api.py                  # ApiGateway stack
│       ├── eventbridge.py          # EventBridge stack
│       ├── graphql.py              # AppSync GraphQL stack
│       ├── s3.py                   # S3 stack
│       ├── stream.py               # DynamoDB Stream stack
│       └── sqs.py                  # SQS stack
└── tests                           # Test folder
    ├── conftest.py                 # Pytest configuration, fixtures, and hooks
    ├── test_repository.py          # Repository tests
    ├── agent                       # Bedrock agent scenario tests
    ├── api                         # API scenario tests
    ├── eventbridge                 # EventBridge scenario tests
    ├── graphql                     # GraphQL scenario tests
    ├── s3                          # S3 scenario tests
    ├── stream                      # DynamoDB Stream scenario tests
    └── sqs                         # SQS scenario tests
```
