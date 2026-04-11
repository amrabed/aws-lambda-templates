# Implementation Plan: GitHub Deploy Workflow

## Overview

Create `.github/workflows/deploy.yml` with OIDC-based AWS authentication, quality gate integration, and conditional stack deployment. Update the Makefile `deploy` target to pass `--require-approval never`. Add structural tests in `tests/test_deploy_workflow.py`.

## Tasks

- [x] 1. Update Makefile deploy target
  - Add `--require-approval never` flag to the `cdk deploy` command in the `deploy` target
  - _Requirements: 5.2_

- [x] 2. Create the deploy workflow file
  - [x] 2.1 Create `.github/workflows/deploy.yml` with triggers and permissions
    - Add `push` trigger scoped to `branches: [main]`
    - Add `workflow_dispatch` trigger with required `choice` input `stack` accepting `api` or `stream`
    - Set top-level `permissions` block to exactly `id-token: write` and `contents: read`
    - _Requirements: 1.1, 1.2, 6.1, 6.2, 6.3_

  - [x] 2.2 Add `check` job that reuses `check.yml`
    - Add `check` job using `uses: ./.github/workflows/check.yml`
    - _Requirements: 2.1, 2.2_

  - [x] 2.3 Add `deploy-api` job
    - Set `needs: check`
    - Set `if:` condition to run on `push` OR (`workflow_dispatch` AND `inputs.stack == 'api'`)
    - Set `AWS_DEFAULT_REGION: ${{ vars.AWS_REGION }}` at job level
    - Add steps: `actions/checkout@v4`, `actions/setup-python@v5` with `python-version: "3.14"`, `make poetry install`, `npm install -g aws-cdk`, `aws-actions/configure-aws-credentials@v4` with `role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}` and `aws-region: ${{ vars.AWS_REGION }}`, then `make deploy STACK=api`
    - Pin all third-party actions to a specific SHA
    - _Requirements: 1.3, 1.4, 3.1, 3.2, 3.3, 3.5, 4.1, 4.2, 4.3, 5.1, 5.4, 6.4_

  - [x] 2.4 Add `deploy-stream` job
    - Set `needs: [check, deploy-api]`
    - Set `if:` condition to run on `push` OR (`workflow_dispatch` AND `inputs.stack == 'stream'`)
    - Mirror the same steps as `deploy-api` but with `STACK=stream`
    - _Requirements: 1.3, 1.4, 3.1, 3.2, 3.3, 3.5, 4.1, 4.2, 4.3, 5.1, 5.4, 6.4_

- [x]* 3. Create structural tests
  - [x]* 3.1 Create `tests/test_deploy_workflow.py` with a pytest fixture that parses the workflow YAML
    - Load `.github/workflows/deploy.yml` once via a session-scoped fixture using PyYAML
    - Add `if __name__ == "__main__": main()` at end of file
    - _Requirements: 1.1, 1.2_

  - [x]* 3.2 Write unit tests for trigger and job structure
    - Test `workflow_dispatch` input `stack` is required, type `choice`, options `["api", "stream"]` — Req 1.2
    - Test `push` trigger is scoped to `branches: [main]` — Req 1.1
    - Test `deploy-api` has `needs: check` and correct `if:` condition — Req 1.3, 1.4, 2.1
    - Test `deploy-stream` has `needs: [check, deploy-api]` and correct `if:` condition — Req 1.3, 1.4, 2.1
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1_

  - [ ]* 3.3 Write unit tests for OIDC and environment setup steps
    - Test each deploy job has a step using `aws-actions/configure-aws-credentials` — Req 3.1
    - Test that step's `role-to-assume` is `${{ secrets.AWS_DEPLOY_ROLE_ARN }}` — Req 3.2
    - Test that step's `aws-region` is `${{ vars.AWS_REGION }}` — Req 3.3
    - Test `setup-python` step uses `python-version: "3.14"` — Req 4.1
    - Test a step runs `make poetry install` — Req 4.2
    - Test a step installs the CDK CLI (contains `aws-cdk`) — Req 4.3
    - Test `deploy-api` step runs `make deploy STACK=api` — Req 5.1
    - Test `deploy-stream` step runs `make deploy STACK=stream` — Req 5.1
    - Test `AWS_DEFAULT_REGION` env is set to `${{ vars.AWS_REGION }}` at job level — Req 5.4
    - Test Makefile `deploy` target contains `--require-approval never` — Req 5.2
    - Test top-level `permissions` contains `id-token: write` and `contents: read` — Req 6.1, 6.2
    - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 5.1, 5.2, 5.4, 6.1, 6.2_

  - [ ]* 3.4 Write property test for Property 1: all third-party actions are pinned
    - **Property 1: All third-party actions are pinned**
    - Collect all `uses:` values from every step in every job; for each value not starting with `./`, assert the `@<ref>` portion is a 40-char hex SHA or a version tag matching `v\d+`; assert no reference ends with `@main`, `@master`, or `@HEAD`
    - **Validates: Requirements 6.4**

  - [ ]* 3.5 Write property test for Property 2: permissions block is exactly least-privilege
    - **Property 2: Permissions block is exactly least-privilege**
    - Load the top-level `permissions` dict and assert it equals exactly `{"id-token": "write", "contents": "read"}` with no extra keys
    - **Validates: Requirements 6.1, 6.2, 6.3**

- [x]* 4. Checkpoint — Ensure all tests pass
  - Run `make test` and confirm all tests in `tests/test_deploy_workflow.py` pass. Ask the user if questions arise.
