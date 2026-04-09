# Requirements Document

## Introduction

This feature adds a GitHub Actions workflow that automates deployment of AWS CDK stacks to AWS when triggered. The workflow authenticates with AWS using OIDC (no long-lived credentials), runs `make deploy` with a specified stack target, and integrates with the existing CI check workflow. It supports deploying either the `api` or `stream` CDK stack, matching the existing `STACK` environment variable convention used in the Makefile.

## Glossary

- **Workflow**: The GitHub Actions YAML file that defines the automated deployment pipeline.
- **CDK_Stack**: One of the two deployable AWS CDK stacks: `api` (ApiGatewayDynamodbStack) or `stream` (DynamodbStreamStack), selected via the `STACK` environment variable.
- **OIDC**: OpenID Connect — the AWS-recommended mechanism for GitHub Actions to assume an IAM role without storing long-lived AWS credentials as secrets.
- **IAM_Role**: An AWS IAM role with the permissions required to deploy CDK stacks, configured to trust GitHub Actions via OIDC.
- **Deployment_Job**: The GitHub Actions job responsible for running the deployment steps.
- **Check_Workflow**: The existing `check.yml` workflow that runs lint and tests (`make lint` and `make test`).

---

## Requirements

### Requirement 1: Workflow Trigger

**User Story:** As a developer, I want the deployment workflow to trigger automatically on pushes to `main` and manually on demand, so that production deployments happen consistently without manual steps.

#### Acceptance Criteria

1. WHEN a commit is pushed to the `main` branch, THE Workflow SHALL start a deployment run.
2. THE Workflow SHALL support manual triggering via `workflow_dispatch` with a required input selecting the target CDK_Stack (`api` or `stream`).
3. WHEN triggered by a push to `main`, THE Workflow SHALL default to deploying all stacks sequentially (`api` then `stream`).
4. WHEN triggered manually via `workflow_dispatch`, THE Workflow SHALL deploy only the CDK_Stack selected by the user input.

---

### Requirement 2: Pre-deployment Quality Gate

**User Story:** As a developer, I want the deployment workflow to run lint and tests before deploying, so that broken code is never deployed to AWS.

#### Acceptance Criteria

1. WHEN the Workflow is triggered, THE Deployment_Job SHALL depend on the Check_Workflow completing successfully before any deployment step runs.
2. IF the Check_Workflow fails, THEN THE Workflow SHALL halt and THE Deployment_Job SHALL not execute.

---

### Requirement 3: AWS Authentication via OIDC

**User Story:** As a platform engineer, I want the workflow to authenticate with AWS using OIDC, so that no long-lived AWS credentials are stored as GitHub secrets.

#### Acceptance Criteria

1. THE Workflow SHALL use the `aws-actions/configure-aws-credentials` action to assume an IAM_Role via OIDC.
2. THE Workflow SHALL read the IAM_Role ARN from a GitHub Actions secret named `AWS_DEPLOY_ROLE_ARN`.
3. THE Workflow SHALL read the target AWS region from a GitHub Actions variable named `AWS_REGION`.
4. IF the OIDC token exchange fails, THEN THE Workflow SHALL fail the Deployment_Job with a non-zero exit code and SHALL NOT proceed to the deploy step.
5. THE Workflow SHALL request the `id-token: write` permission required for OIDC authentication.

---

### Requirement 4: Environment Setup

**User Story:** As a developer, I want the workflow to install all project dependencies before deploying, so that CDK and Poetry-managed packages are available during deployment.

#### Acceptance Criteria

1. THE Deployment_Job SHALL use Python 3.14 to match the version declared in `pyproject.toml`.
2. THE Deployment_Job SHALL install Poetry and all project dependencies by running `make poetry install`.
3. THE Deployment_Job SHALL install the AWS CDK CLI so that `cdk` is available on the PATH during deployment.

---

### Requirement 5: CDK Stack Deployment

**User Story:** As a developer, I want the workflow to deploy the correct CDK stack using `make deploy`, so that the deployment is consistent with local developer workflows.

#### Acceptance Criteria

1. WHEN deploying a CDK_Stack, THE Deployment_Job SHALL run `make deploy STACK=<stack>` where `<stack>` is the target stack name.
2. THE Deployment_Job SHALL pass `--require-approval never` to CDK (via the Makefile or environment) so that the deployment does not wait for interactive confirmation.
3. WHEN `make deploy` exits with a non-zero code, THE Workflow SHALL mark the Deployment_Job as failed.
4. THE Deployment_Job SHALL set the `AWS_DEFAULT_REGION` environment variable to the value of the `AWS_REGION` GitHub Actions variable for all steps.

---

### Requirement 6: Workflow Permissions and Security

**User Story:** As a platform engineer, I want the workflow to follow least-privilege principles, so that the GitHub Actions runner has only the permissions it needs.

#### Acceptance Criteria

1. THE Workflow SHALL grant `id-token: write` permission to enable OIDC token issuance.
2. THE Workflow SHALL grant `contents: read` permission to allow repository checkout.
3. THE Workflow SHALL NOT grant any additional permissions beyond those listed in criteria 1 and 2.
4. THE Workflow SHALL pin all third-party GitHub Actions to a specific SHA or version tag to prevent supply-chain attacks.
