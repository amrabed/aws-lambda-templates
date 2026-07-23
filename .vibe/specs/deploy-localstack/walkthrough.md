# Walkthrough: Deploy Lambda Stacks to Local using LocalStack

We have added support for deploying and tearing down AWS CDK Lambda stacks locally using LocalStack.

## Changes Made

### Configuration & Infrastructure

- Created `compose.yml` configured to spin up LocalStack (gateway on port 4566).
- Created `.env.local.example` with defaults for local execution and LocalStack auth token configuration.
- Updated `mise.toml`:
  - Added `[tasks."local:up"]` task to start LocalStack container with `.env.local`.
  - Added `[tasks."local:down"]` task to stop LocalStack container with `.env.local`.
  - Added `[tasks."local:deploy"]` task with aliases `local` and `dl` to deploy CDK stacks locally via `aws-cdk-local` (depends on `install-cdk`, `local:up`).
  - Added `[tasks."local:destroy"]` task with alias `Dl` to destroy stacks from LocalStack via `aws-cdk-local` (depends on `install-cdk`, `local:up`).
  - Renamed documentation local preview task to `[tasks.docs-local]`.

### Documentation

- Updated `docs/README.md`:
  - Added step to copy `.env.local.example` to `.env.local` and set `LOCALSTACK_AUTH_TOKEN` from [app.localstack.cloud](https://app.localstack.cloud).
  - Added Docker under Local environment prerequisites.
  - Added "Deploy a stack locally (LocalStack)" and "Destroy a local stack" sections with `local:up`, `local:deploy`, `local:destroy`, and `local:down`.
  - Updated Project Structure tree diagram with `compose.yml`.
- Updated `AGENTS.md`:
  - Added `.env.local` token guidance, LocalStack & local CDK deployment commands (`mise run local:up`, `mise run local:deploy`, `mise run local:destroy`) and aliases.

### Specifications

- Updated `.vibe/specs/deploy-localstack/`:
  - `requirements.md`
  - `design.md`
  - `plan.md`
  - `tasks.md`
  - `walkthrough.md`

## Verification Results

### Automated Verification

1. `mise run lint`: Format & lint validations passed.
2. `mise run test`: All 71 unit tests passed with 93% coverage.

### Manual Verification

- Verified `.env.local.example` content and task execution configuration.
