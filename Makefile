.PHONY: help
help: # Show available targets
	@grep -E '^[a-zA-Z_-]+:.*# .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*# "}; {printf "  %-12s %s\n", $$1, $$2}'

NAME ?= templates
DESCRIPTION ?= AWS Lambda Templates
AUTHOR ?= Amr Abed
EMAIL ?= amrabed
GITHUB ?= amrabed
SOURCE ?= $(shell echo ${NAME} | tr '-' '_' | tr '[:upper:]' '[:lower:]')

.PHONY: new
new: # Create new Lambda function template (usage: make new template=<name>)
	@[ -n "$(template)" ] || { echo "Usage: make new template=<name>"; exit 1; }
	uv run new -n $(template)

.PHONY: project
project: # Rename project (run once)
	@if [ -d templates ]; then mv templates ${SOURCE}; fi
	@sed -i '' 's/^::: templates\.app/::: ${SOURCE}\.app/' docs/reference/app.md
	@sed -i '' 's/^repo_name: .*/repo_name: ${GITHUB}\/${NAME}/' mkdocs.yml
	@sed -i '' 's/^repo_url: .*/repo_url: https:\/\/github.com\/${GITHUB}\/${NAME}/' mkdocs.yml
	@sed -i '' 's/^source = \[.*\]/source = \["${SOURCE}"\]/' pyproject.toml
	@sed -i '' 's/^name = ".*"/name = "${SOURCE}"/' pyproject.toml
	@sed -i '' 's/^description = ".*"/description = "${DESCRIPTION}"/' pyproject.toml
	@sed -i '' 's/^authors = \[.*\]/authors = \[{name = "${AUTHOR}", email = "${EMAIL}"}\]/' pyproject.toml
	@sed -i '' 's/^# .*/# ${DESCRIPTION}/' docs/README.md
	@sed -i '' 's/@.*/@${GITHUB}/' .github/CODEOWNERS
	@sed -i '' 's/^github: \[.*\]/github: \[${GITHUB}\]/' .github/FUNDING.yml

.PHONY: uv
uv: # Install uv if not already installed
	pipx install uv

venv: # Activate virtual environment
	uv venv --clear
	. .venv/bin/activate

install: # Install dependencies and project
	uv sync

update: # Update dependencies
	uv lock --upgrade

precommit: # Install pre-commit hooks
	uv run pre-commit autoupdate
	uv run pre-commit install

dev: uv venv precommit install

lint:
	uv run ruff format
	uv run ruff check --fix
	uv run ruff format
# 	uv run pyright

coverage:
	uv run coverage run -m pytest .
	uv run coverage report -m
	uv run coverage xml

test: coverage

install-docs:
	uv sync --group docs

.PHONY: docs
docs: # Build and deploy documentation to GitHub pages
	uv run mkdocs gh-deploy --force

local: # Serve documentation on a local server
	uv run mkdocs serve

# CDK stacks mapping
CDK_STACK                        = \$(STACK_MAP_\$(STACK))
STACK_MAP_agent				  	 = BedrockAgentStack
STACK_MAP_api                    = ApiGatewayDynamodbStack
STACK_MAP_stream                 = DynamodbStreamStack
STACK_MAP_eventbridge 			 = EventBridgeApiCallerStack
STACK_MAP_graphql                = AppSyncDynamodbStack
STACK_MAP_s3                     = S3SqsStack
STACK_MAP_sqs                    = SqsStack

.PHONY: deploy
deploy: # Deploy an CDK stack
	@[ -n "$(STACK)" ] || { echo "Usage: make deploy STACK=<agent|api|eventbridge|graphql|s3|sqs|stream>"; exit 1; }
	@[ -n "\$(CDK_STACK)" ] || { echo "Error: unknown stack '\$(STACK)'"; exit 1; }
	STACK=\$(STACK) uv run cdk deploy --app "python infra/app.py" --require-approval never \$(CDK_STACK) \
		\$(if \$(AWS_PROFILE),--profile \$(AWS_PROFILE),)

.PHONY: destroy
destroy: # Destroy a deployed CDK stack
	@[ -n "$(STACK)" ] || { echo "Usage: make destroy STACK=<agent|api|eventbridge|graphql|s3|sqs|stream>"; exit 1; }
	@[ -n "\$(CDK_STACK)" ] || { echo "Error: unknown stack '\$(STACK)'"; exit 1; }
	STACK=\$(STACK) uv run cdk destroy --force --app "python infra/app.py" \$(CDK_STACK) \
		\$(if \$(AWS_PROFILE),--profile \$(AWS_PROFILE),)

all: install lint test
