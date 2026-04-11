# Implementation Plan: cdk-deploy-destroy-targets

## Overview

Create `infra/app.py` as the CDK app entry point and add `deploy`/`destroy` targets to the Makefile.

## Tasks

- [x] 1. Create `infra/app.py` CDK entry point
  - Implement `STACK_REGISTRY` dict mapping `"api"` → `ApiGatewayDynamodbStack` and `"stream"` → `DynamodbStreamStack`
  - Read `STACK` from `os.environ`; call `sys.exit(1)` with a descriptive message if missing or not in registry
  - Instantiate the resolved stack class using the class name as the construct ID, then call `app.synth()`
  - _Requirements: 4.1, 4.2, 4.3_

  - [ ]* 1.1 Write unit tests for `infra/app.py` (`tests/infra/test_app.py`)
    - Create `tests/infra/__init__.py` and `tests/infra/test_app.py`
    - Test `STACK=api` → exactly one stack, instance of `ApiGatewayDynamodbStack`
    - Test `STACK=stream` → exactly one stack, instance of `DynamodbStreamStack`
    - Test `STACK` unset → `SystemExit` with non-zero code
    - Test `STACK=unknown` → `SystemExit` with non-zero code
    - Test registry keys are exactly `{"api", "stream"}` (validates 3.1, 3.2)
    - End file with `if __name__ == "__main__": main()`
    - _Requirements: 4.1, 4.2, 4.3, 3.1, 3.2_

  - [ ]* 1.2 Write property test for `infra/app.py` (`tests/infra/test_app_properties.py`)
    - **Property 1: Valid stack name instantiates exactly the correct stack class**
    - `@given(st.sampled_from(list(STACK_REGISTRY.items())))` — for any `(name, cls)` pair, app produces exactly one stack that is an instance of `cls`
    - **Validates: Requirements 1.1, 2.1, 3.1, 3.2, 4.1, 4.2**
    - **Property 2: Invalid or missing STACK causes non-zero exit**
    - `@given(st.text().filter(lambda s: s not in STACK_REGISTRY))` — for any string not in registry, app raises `SystemExit` with non-zero code
    - **Validates: Requirements 1.2, 1.3, 2.2, 2.3, 4.3**
    - Tag each test with the comment: `# Feature: cdk-deploy-destroy-targets, Property <N>: <property_text>`
    - End file with `if __name__ == "__main__": main()`

- [x] 2. Checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. Add `deploy` and `destroy` targets to `Makefile`
  - Add `STACK_MAP_api`, `STACK_MAP_stream`, and `CDK_STACK` variable definitions
  - Add `deploy` target: validate `STACK` is set, validate `CDK_STACK` is non-empty, invoke `cdk deploy --app "python infra/app.py" $(CDK_STACK)` with optional `--profile $(AWS_PROFILE)`
  - Add `destroy` target: same validation, invoke `cdk destroy --force --app "python infra/app.py" $(CDK_STACK)` with optional `--profile $(AWS_PROFILE)`
  - Add `deploy` and `destroy` to `.PHONY`
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3_

- [x] 4. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Property tests use Hypothesis (already a dev dependency)
- The Makefile and `infra/app.py` both validate `STACK` independently — Makefile is the first line of defence
