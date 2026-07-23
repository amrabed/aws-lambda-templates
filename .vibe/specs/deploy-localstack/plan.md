# Implementation Plan - Deploy Lambda Stacks to Local using LocalStack

Enable local deployment and teardown of AWS CDK Lambda stacks using LocalStack and `aws-cdk-local`.

## User Review Required

> [!IMPORTANT]
> Developers must copy `.env.local.example` to `.env.local` and set `LOCALSTACK_AUTH_TOKEN` obtained from [app.localstack.cloud](https://app.localstack.cloud).

## Proposed Changes

### Configuration & Infrastructure

#### [NEW] [compose.yml](file:///Users/amrabed/Library/CloudStorage/OneDrive-Personal/code/aws-lambda-templates/compose.yml)

- Add standard LocalStack container definition exposing port `4566`.

#### [NEW] [.env.local.example](file:///Users/amrabed/Library/CloudStorage/OneDrive-Personal/code/aws-lambda-templates/.env.local.example)

- Add template environment file with `LOCALSTACK_AUTH_TOKEN`, local AWS credentials, and endpoint URLs.

#### [MODIFY] [mise.toml](file:///Users/amrabed/Library/CloudStorage/OneDrive-Personal/code/aws-lambda-templates/mise.toml)

- Add shell aliases `local = "mise run local:deploy"`, `dl = "mise run local:deploy"`, and `Dl = "mise run local:destroy"`.
- Rename documentation local serve task to `[tasks.docs-local]`.
- Add `[tasks."local:up"]` to start LocalStack via `docker compose --env-file .env.local up -d --wait localstack`.
- Add `[tasks."local:down"]` to stop LocalStack via `docker compose --env-file .env.local down localstack`.
- Add `[tasks."local:deploy"]` (aliases `local`, `dl`) to deploy stacks locally using `aws-cdk-local`.
- Add `[tasks."local:destroy"]` (alias `Dl`) to destroy stacks locally using `aws-cdk-local`.

---

### Documentation

#### [MODIFY] [docs/README.md](file:///Users/amrabed/Library/CloudStorage/OneDrive-Personal/code/aws-lambda-templates/docs/README.md)

- Update Prerequisites section to include LocalStack / Docker.
- Add step to copy `.env.local.example` to `.env.local` and obtain token from `app.localstack.cloud`.
- Add "Deploy stack to local (LocalStack)" and "Destroy local stack" sub-sections under Infrastructure deployment options.
- Update project structure tree diagram to include `compose.yml` and `.vibe/specs`.

#### [MODIFY] [AGENTS.md](file:///Users/amrabed/Library/CloudStorage/OneDrive-Personal/code/aws-lambda-templates/AGENTS.md)

- Add instructions to setup `.env.local` with token from `app.localstack.cloud`.
- Add `mise run local:deploy`, `mise run local:destroy`, `mise run local:up`, and `mise run local:down` to Common Commands list.

---

### Specifications

#### [NEW] [.vibe/specs/deploy-localstack/requirements.md](file:///Users/amrabed/Library/CloudStorage/OneDrive-Personal/code/aws-lambda-templates/.vibe/specs/deploy-localstack/requirements.md)

#### [NEW] [.vibe/specs/deploy-localstack/design.md](file:///Users/amrabed/Library/CloudStorage/OneDrive-Personal/code/aws-lambda-templates/.vibe/specs/deploy-localstack/design.md)

#### [NEW] [.vibe/specs/deploy-localstack/plan.md](file:///Users/amrabed/Library/CloudStorage/OneDrive-Personal/code/aws-lambda-templates/.vibe/specs/deploy-localstack/plan.md)

#### [NEW] [.vibe/specs/deploy-localstack/tasks.md](file:///Users/amrabed/Library/CloudStorage/OneDrive-Personal/code/aws-lambda-templates/.vibe/specs/deploy-localstack/tasks.md)

#### [NEW] [.vibe/specs/deploy-localstack/walkthrough.md](file:///Users/amrabed/Library/CloudStorage/OneDrive-Personal/code/aws-lambda-templates/.vibe/specs/deploy-localstack/walkthrough.md)

## Verification Plan

### Automated Tests

- Run `mise run lint` (ruff format and check) to confirm code quality and formatting.
- Run `mise run test` to verify pytest suite execution.

### Manual Verification

- Test synthesizing / validating localstack CDK command syntax: `STACK=api uv run npx --package=aws-cdk --package=aws-cdk-local cdklocal synth`.
