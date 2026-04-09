# Requirements Document

## Introduction

This feature adds `deploy` and `destroy` Make targets to the project's Makefile, enabling developers to deploy and tear down AWS Lambda stacks using AWS CDK from a single, consistent interface. The targets must support selecting which CDK stack to operate on (api or stream), accept an optional AWS profile, and integrate cleanly with the existing `make` workflow.

## Glossary

- **Makefile**: The project's top-level `Makefile` used to automate common developer workflows.
- **CDK**: AWS Cloud Development Kit — the infrastructure-as-code framework used under `infra/`.
- **Stack**: A deployable CDK unit. The project currently defines two stacks: `api` (ApiGatewayDynamodbStack) and `stream` (DynamodbStreamStack).
- **Stack_Name**: The logical identifier used to select a stack, corresponding to the stack module name under `infra/stacks/` (e.g., `api`, `stream`).
- **AWS_Profile**: An optional named AWS CLI profile used to authenticate CDK commands.
- **Deploy_Target**: The `deploy` Make target that synthesises and deploys a CDK stack to AWS.
- **Destroy_Target**: The `destroy` Make target that tears down a previously deployed CDK stack from AWS.

## Requirements

### Requirement 1: Deploy a CDK Stack

**User Story:** As a developer, I want to run `make deploy STACK=<stack>` to deploy a Lambda stack to AWS, so that I can provision infrastructure without remembering CDK CLI syntax.

#### Acceptance Criteria

1. WHEN the `deploy` target is invoked with a valid `STACK` value, THE Deploy_Target SHALL execute `cdk deploy` for the corresponding CDK stack.
2. WHEN the `deploy` target is invoked without a `STACK` value, THE Deploy_Target SHALL print a usage error message and exit with a non-zero status code.
3. WHEN the `deploy` target is invoked with a `STACK` value that does not match any defined stack, THE Deploy_Target SHALL print an error message identifying the invalid stack name and exit with a non-zero status code.
4. WHERE an `AWS_PROFILE` variable is provided, THE Deploy_Target SHALL pass the profile to the CDK CLI via the `--profile` flag.
5. WHEN `cdk deploy` fails, THE Deploy_Target SHALL propagate the non-zero exit code to the calling shell.

### Requirement 2: Destroy a CDK Stack

**User Story:** As a developer, I want to run `make destroy STACK=<stack>` to tear down a deployed Lambda stack, so that I can clean up AWS resources without remembering CDK CLI syntax.

#### Acceptance Criteria

1. WHEN the `destroy` target is invoked with a valid `STACK` value, THE Destroy_Target SHALL execute `cdk destroy` with the `--force` flag for the corresponding CDK stack.
2. WHEN the `destroy` target is invoked without a `STACK` value, THE Destroy_Target SHALL print a usage error message and exit with a non-zero status code.
3. WHEN the `destroy` target is invoked with a `STACK` value that does not match any defined stack, THE Destroy_Target SHALL print an error message identifying the invalid stack name and exit with a non-zero status code.
4. WHERE an `AWS_PROFILE` variable is provided, THE Destroy_Target SHALL pass the profile to the CDK CLI via the `--profile` flag.
5. WHEN `cdk destroy` fails, THE Destroy_Target SHALL propagate the non-zero exit code to the calling shell.

### Requirement 3: Stack Selection Mapping

**User Story:** As a developer, I want the Make targets to map short stack names (e.g., `api`, `stream`) to the correct CDK stack class names, so that I don't need to know the full CDK construct ID.

#### Acceptance Criteria

1. THE Makefile SHALL define a mapping from the `api` Stack_Name to the `ApiGatewayDynamodbStack` CDK stack identifier.
2. THE Makefile SHALL define a mapping from the `stream` Stack_Name to the `DynamodbStreamStack` CDK stack identifier.
3. WHEN a new stack module is added under `infra/stacks/`, THE Makefile SHALL require only a single-line addition to the mapping to support the new stack in the `deploy` and `destroy` targets.

### Requirement 4: CDK App Entry Point

**User Story:** As a developer, I want a CDK app entry point that instantiates the selected stack, so that `cdk deploy` and `cdk destroy` can target individual stacks without deploying all stacks at once.

#### Acceptance Criteria

1. THE CDK_App SHALL accept a `STACK` environment variable to determine which stack to instantiate.
2. WHEN the `STACK` environment variable is set to a valid Stack_Name, THE CDK_App SHALL instantiate only the corresponding CDK stack.
3. WHEN the `STACK` environment variable is not set or is set to an unrecognised value, THE CDK_App SHALL exit with a descriptive error message and a non-zero status code.
4. THE Makefile SHALL pass the `STACK` variable to the CDK app via the `--context` flag or environment variable so that the CDK app can resolve the correct stack.
