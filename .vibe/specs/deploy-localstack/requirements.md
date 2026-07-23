# Requirements: Deploy Lambda Stacks to Local via LocalStack

## Overview

Enable developers to deploy and tear down AWS CDK Lambda stacks locally using LocalStack without requiring an active AWS cloud account or active AWS credentials.

## Functional Requirements

1. **Environment & Auth Token Setup**:
   - Provide `.env.local.example` with defaults for LocalStack and local CDK deployment.
   - Instruct developers to copy `.env.local.example` to `.env.local` and obtain an auth token from [app.localstack.cloud](https://app.localstack.cloud) to populate `LOCALSTACK_AUTH_TOKEN`.
2. **Local Stack Deployment**:
   - Provide a `local:deploy` task in `mise.toml` that deploys any CDK stack defined under `infra/stacks/` to a local LocalStack instance.
   - Command syntax: `mise run local:deploy <stack>` (alias `local <stack>` or `dl <stack>`).
3. **Local Stack Destruction**:
   - Provide a `local:destroy` task in `mise.toml` that destroys a deployed stack from LocalStack.
   - Command syntax: `mise run local:destroy <stack>` (alias `Dl <stack>`).
4. **LocalStack Container Management**:
   - Provide a standard `compose.yml` file configuring LocalStack.
   - Provide `local:up` (`mise run local:up`) to start LocalStack with `.env.local`.
   - Provide `local:down` (`mise run local:down`) to stop LocalStack.
5. **Documentation Updates**:
   - Update `docs/README.md` to document LocalStack setup, `.env.local` configuration, token retrieval from app.localstack.cloud, prerequisites, and usage of `local:deploy`, `local:destroy`, `local:up`, and `local:down`.
   - Update `AGENTS.md` to include local deployment environment setup, commands, aliases (`local`, `dl`, `Dl`), and instructions for AI agents.

## Non-Functional Requirements

- Maintain backward compatibility with existing cloud CDK deployment tasks (`mise run deploy` and `mise run destroy`).
- Pass all project linting (`mise run lint`) and tests (`mise run test`).
