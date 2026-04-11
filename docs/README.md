# AWS Lambda Templates - Python
[![Python](https://img.shields.io/badge/python-3.14+-3776AB.svg?logo=python&style=flat-square)](https://python.org)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-D7FF64.svg?logo=ruff&style=flat-square)](https://docs.astral.sh/ruff)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](LICENSE.md)

Production-ready Python AWS Lambda templates for different scenarios. 
See available templates [here](template/index.md).


## Features

All templates come pre-wired with:

- Clean AWS Lambda code following best practices using [AWS Lambda Powertools](https://docs.aws.amazon.com/powertools/python)
- Infrastructure as code using [AWS CDK](https://aws.amazon.com/cdk/)
- Testing using [pytest](https://pytest.org) and [Hypothesis](https://hypothesis.readthedocs.io) for property-based testing
- Workflow automation using [GitHub Actions](https://github.com/features/actions)
- Automatic documentation from code using [MkDocs](https://www.mkdocs.org) and [mkdocstrings](https://mkdocstrings.github.io)
- Packaging and dependency management using [Poetry](https://python-poetry.org)
- Code coverage using [coverage](https://coverage.readthedocs.io)
- Formatting, import sorting, and linting using [ruff](https://docs.astral.sh/ruff)
- Type checking using [pyright](https://microsoft.github.io/pyright)
- Pre-commit validations using [pre-commit](https://pre-commit.com)
- Automated dependency updates using [Dependabot](https://docs.github.com/en/code-security/dependabot)
- Dockerized development environment using [Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- Documentation auto-deployment to [GitHub Pages](https://pages.github.com)
- App container using [Docker](https://docker.com)


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
- Poetry
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

### Deploy a stack
```bash
make deploy STACK=api
# or
make deploy STACK=stream
# or
make deploy STACK=s3
```

Pass `AWS_PROFILE` to use a named AWS CLI profile:
```bash
make deploy STACK=api AWS_PROFILE=my-profile
```

### Destroy a stack
```bash
make destroy STACK=api
# or
make destroy STACK=stream AWS_PROFILE=my-profile
# or
make destroy STACK=s3 AWS_PROFILE=my-profile
```

## Generating documentation

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

## CDK Infrastructure Deployment

Infrastructure is defined as AWS CDK stacks under [`infra/stacks/`](/infra/stacks). 
The CDK entry point is [`infra/app.py`](/infra/app.py). 
The `STACK` environment variable selects which stack to synthesise.

Stack | Class | Deploy command
--- | --- | ---
API | `ApiGatewayDynamodbStack` | `make deploy STACK=api`
Bedrock Agent | `BedrockAgentStack` | `make deploy STACK=bedrock-agent`
EventBridge | `EventBridgeApiCallerStack` | `make deploy STACK=eventbridge`
Stream | `DynamodbStreamStack` | `make deploy STACK=stream`
S3 | `S3SqsStack` | `make deploy STACK=s3`
SQS | `SqsLambdaDynamodbStack` | `make deploy STACK=sqs`

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
│   └── settings.json               # VS Code settings
├── .dockerignore                   # Docker-ignored file list
├── compose.yml                     # Docker Compose file
├── Dockerfile                      # App container Dockerfile
├── LICENSE                         # Project license
├── Makefile                        # Make commands
├── pyproject.toml                  # Configuration file for different tools
├── mkdocs.yml                      # MkDocs configuration file
├── docs                            # Documentation folder
│   ├── README.md                   # Read-me file & documentation home page
│   ├── CONTRIBUTING.md             # Contributing guidelines
│   ├── template                    # Templates summary page
│   │   ├── api.md                  # API documentation page
│   │   ├── eventbridge.md          # EventBridge documentation page
│   │   ├── s3.md                   # S3 documentation page
│   │   ├── stream.md               # Stream documentation page
│   │   └── sqs.md                  # S3 documentation page
│   └── reference                   # Reference section
│       ├── repository.md           # Repository reference page
│       ├── api.md                  # API scenario reference page
│       ├── eventbridge.md          # EventBridge scenario reference page
│       ├── s3.md                   # S3 scenario reference page
│       ├── stream.md               # Stream scenario reference page
│       └── sqs.md                  # SQS scenario reference page
├── templates                       # Main package
│   ├── queue.py                    # SQS queue interaction
│   ├── repository.py               # DynamoDB repository
│   ├── api                         # API request handler
│   ├── eventbridge                 # EventBridge event handler
    ├── s3                          # S3 event handler
│   ├── stream                      # DynamoDB stream batch processor
    ├── bedrock_agent               # Bedrock agent function handler
    └── sqs                         # SQS message handler
├── infra                           # AWS CDK infrastructure
│   ├── app.py                      # CDK entry point
│   └── stacks                      # CDK stack definitions
│       ├── api.py                  # ApiGateway stack
│       ├── bedrock_agent.py        # Bedrock agent stack
│       ├── evetbridge.py           # EventBridge stack
        ├── s3.py                   # S3 stack
│       ├── stream.py               # DynamoDB Stream stack
        └── sqs.py                  # SQS stack
└── tests                           # Test folder
    ├── conftest.py                 # Pytest configuration, fixtures, and hooks
    ├── test_repository.py          # Repository tests
    ├── api                         # API scenario tests
    ├── bedrock_agent               # Bedrock agent scenario tests
    ├── eventbridge                 # EventBridge scenario tests
    ├── s3                          # S3 scenario tests
    ├── stream                      # DynamoDB Stream scenario tests
    └── sqs                         # SQS scenario tests
```
