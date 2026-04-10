# Implementation Plan: S3 → SQS Lambda Template

## Overview

Implement `templates/s3/` — a reusable Lambda handler that receives S3 object-creation events, transforms each record into a typed `ProcessedMessage`, and publishes it to SQS. Fully instrumented with AWS Lambda Powertools and covered by pytest + Hypothesis property tests.

## Tasks

- [x] 1. Create module skeleton and settings
- [x] 2. Implement data models
- [x] 3. Implement handler internals
- [x] 4. Implement `lambda_handler` orchestration
- [x] 5. Checkpoint — verify module imports cleanly
- [x] 6. Write example-based unit tests
- [x] 7. Final checkpoint — ensure all tests pass
- [x] 8. Add CDK stack file under `infra/stacks/s3.py`
- [x] 9. Add documentation markdown file under `docs/template/s3.md`
- [x] 10. Update `infra/app.py`, `docs/template/index.md`, `docs/README.md`, `mkdocs.yml` to include this template
