# Implementation Plan: eventbridge-api-caller

## Overview

Implement the `eventbridge-api-caller` Lambda scenario template: a function triggered by an EventBridge rule that loads an auth token from Secrets Manager, calls an external HTTP API, and persists the response to a DynamoDB table using the shared `Repository` class. Includes CDK stack, unit tests, property-based tests, documentation, and Makefile wiring.

## Tasks

- [x] 1. Create feature branch
  - Run `git checkout -b feat/eventbridge-api-caller`
  - _Requirements: (prerequisite for all work)_

- [x] 2. Scaffold `templates/eventbridge/` module
  - [x] 2.1 Create `templates/eventbridge/settings.py`
    - Define `Settings(BaseSettings, case_sensitive=False)` with fields: `api_url`, `secret_name`, `service_name`, `metrics_namespace`, `table_name`
    - Every field must use `Field(description="...")`
    - Raises `ValidationError` on cold-start if any variable is absent
    - _Requirements: 5.1, 5.2, 5.3, 11.3_

  - [x] 2.2 Create `templates/eventbridge/models.py`
    - Define `EventBridgeEvent(BaseModel, populate_by_name=True, alias_generator=to_camel)` with fields: `source`, `detail_type`, `detail`
    - Define `ApiResponse(BaseModel, populate_by_name=True, alias_generator=to_camel)` with field: `status`
    - Every field must use `Field(description="...")`
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 2.3 Create `templates/eventbridge/secret_client.py`
    - Define `SecretClient` with `get_token(secret_name: str) -> str` using `SecretsProvider` from `aws_lambda_powertools.utilities.parameters`
    - Propagate exceptions unchanged on failure
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 2.4 Create `templates/eventbridge/api_client.py`
    - Define `ApiClient` with `call(url: str, token: str) -> dict[str, Any]` using `urllib.request` only
    - Include `Authorization: Bearer {token}` header on every request
    - Raise `HTTPError` for non-2xx responses; propagate `URLError`/`TimeoutError` unchanged
    - _Requirements: 3.1, 3.2, 3.4, 3.5, 3.6_

  - [x] 2.5 Create `templates/eventbridge/handler.py`
    - Instantiate `Settings`, `Logger`, `Tracer`, `Metrics`, `SecretClient`, `ApiClient` at module level (cold-start)
    - Define `Handler` class with `handle(event: EventBridgeEvent) -> ApiResponse` decorated with `@tracer.capture_method`
    - Invocation flow: `get_token` → `api_client.call` → parse `ApiResponse` → emit `ApiCallSuccess` metric
    - On any exception from token/API steps: emit `ApiCallFailure` metric, log error, re-raise
    - Define module-level `main(event: dict, context: LambdaContext) -> None` decorated with `@logger.inject_lambda_context`, `@tracer.capture_lambda_handler`, `@metrics.log_metrics`
    - In `main`: validate event with `EventBridgeEvent.model_validate`; on `ValidationError` log and return without calling handler
    - _Requirements: 1.1, 1.2, 1.3, 2.3, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 2.6 Wire DynamoDB persistence into `handler.py`
    - Import `Repository` from `templates.repository` and instantiate at module level: `repository = Repository(settings.table_name)`
    - Pass `repository` into `Handler.__init__` alongside `secret_client` and `api_client`
    - After parsing `ApiResponse`, call `repository.put_item(response.model_dump())`
    - On `put_item` failure: emit `ApiCallFailure` metric, log error, re-raise
    - _Requirements: 11.1, 11.2, 11.3, 11.4_

  - [x] 2.7 Create `templates/eventbridge/__init__.py`
    - Empty init to make the directory a package
    - _Requirements: (module structure)_

- [x] 3. Create CDK stack and register it
  - [x] 3.1 Create `infra/stacks/eventbridge.py`
    - Define `EventBridgeApiCallerStack(Stack)` provisioning:
      - `aws_lambda.Function` with `Runtime.PYTHON_3_13`, handler `templates.eventbridge.handler.main`, `Code.from_asset(".")`
      - `aws_dynamodb.Table` with `partition_key=Attribute(name="id", type=AttributeType.STRING)` and `RemovalPolicy.DESTROY`
      - `table.grant_write_data(function)` granting `dynamodb:PutItem`
      - Environment variables: `API_URL`, `SECRET_NAME`, `SERVICE_NAME`, `METRICS_NAMESPACE`, `TABLE_NAME` (set to `table.table_name`)
      - `aws_events.Rule` with `Schedule.rate(Duration.minutes(5))` targeting the Lambda function
      - `aws_secretsmanager.Secret` (or reference by name) with `secret.grant_read(function)` for `secretsmanager:GetSecretValue`
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8_    - `aws_dynamodb.Table` with `partition_key=Attribute(name="id", type=AttributeType.STRING)` and `RemovalPolicy.DESTROY`
      - `table.grant_write_data(function)` granting `dynamodb:PutItem`
      - Environment variables: `API_URL`, `SECRET_NAME`, `SERVICE_NAME`, `METRICS_NAMESPACE`, `TABLE_NAME` (set to `table.table_name`)
      - `aws_events.Rule` with `Schedule.rate(Duration.minutes(5))` targeting the Lambda function
      - `aws_secretsmanager.Secret` (or reference by name) with `secret.grant_read(function)` for `secretsmanager:GetSecretValue`
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 11.3_

  - [x] 3.2 Register stack in `infra/app.py`
    - Add `from infra.stacks.eventbridge import EventBridgeApiCallerStack`
    - Add `"eventbridge-api-caller": EventBridgeApiCallerStack` to `STACK_REGISTRY`
    - _Requirements: 7.5_

- [x] 4. Checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Write unit tests
  - [x] 5.1 Create `tests/eventbridge/__init__.py`
    - Empty init file
    - _Requirements: (test structure)_

  - [x] 5.2 Create `tests/eventbridge/test_handler.py`
    - Add `autouse` fixture that sets all required env vars via `monkeypatch.setenv`: `API_URL`, `SECRET_NAME`, `SERVICE_NAME`, `METRICS_NAMESPACE`, `TABLE_NAME`
    - Mock `handler.secret_client`, `handler.api_client`, and `handler.repository` via `mocker.patch.object` on the module-level instances
    - Cover: successful invocation (token loaded, API called, `ApiCallSuccess` metric emitted, `repository.put_item` called with `response.model_dump()`)
    - Cover: secret loading failure (`SecretClient.get_token` raises → handler re-raises, `ApiCallFailure` emitted)
    - Cover: API non-2xx response (`ApiClient.call` raises `HTTPError` → handler re-raises, `ApiCallFailure` emitted)
    - Cover: API network exception (`ApiClient.call` raises `URLError` → handler re-raises, `ApiCallFailure` emitted)
    - Cover: invalid EventBridge event (missing required field → handler returns without calling `ApiClient`)
    - Cover: DynamoDB write failure (`repository.put_item` raises → handler re-raises, `ApiCallFailure` emitted)
    - End file with `if __name__ == "__main__": main()`
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 11.1, 11.4_

- [x] 6. Write property-based tests
  - [x] 6.1 Create `tests/eventbridge/test_properties.py`
    - Use `hypothesis` with `@settings(max_examples=100)` on every test
    - Tag each test with a comment: `# Feature: eventbridge-api-caller, Property {N}: {property_text}`
    - Add `autouse` fixture setting all required env vars via `monkeypatch.setenv` (including `TABLE_NAME`)

  - [ ]* 6.2 Write property test for valid event shapes (Property 1)
    - **Property 1: Handler accepts any valid EventBridge event shape**
    - Use `st.text()` for `source`/`detailType`, `st.dictionaries(st.text(), st.text())` for `detail`
    - Assert `EventBridgeEvent.model_validate` succeeds and `ApiClient.call` is invoked
    - **Validates: Requirements 1.2**

  - [ ]* 6.3 Write property test for invalid event prevents API call (Property 2)
    - **Property 2: Invalid event prevents ApiClient call**
    - Use `st.fixed_dictionaries` with one required key removed per run
    - Assert `ApiClient.call` is never invoked
    - **Validates: Requirements 1.3**

  - [ ]* 6.4 Write property test for secret exception propagation (Property 3)
    - **Property 3: SecretClient exception propagates**
    - Use `st.from_type(Exception)` for exception type raised by `get_token`
    - Assert handler raises (does not swallow)
    - **Validates: Requirements 2.3**

  - [ ]* 6.5 Write property test for Bearer token header (Property 4)
    - **Property 4: Bearer token header for any token string**
    - Use `st.text(min_size=1)` for token
    - Assert `Authorization` header value equals `f"Bearer {token}"`
    - **Validates: Requirements 3.2**

  - [ ]* 6.6 Write property test for 2xx response parsed into ApiResponse (Property 5)
    - **Property 5: 2xx response parsed into ApiResponse**
    - Use `st.integers(200, 299)` for status code, `st.text(min_size=1)` for status field
    - Assert `ApiResponse.model_validate` succeeds without raising
    - **Validates: Requirements 3.3**

  - [ ]* 6.7 Write property test for ApiClient failure propagation (Property 6)
    - **Property 6: ApiClient failure propagates exception**
    - Use `st.integers(400, 599)` for non-2xx codes
    - Assert handler raises on any `ApiClient.call` failure
    - **Validates: Requirements 3.4, 3.5**

  - [ ]* 6.8 Write property test for missing env var raises ValidationError (Property 7)
    - **Property 7: Missing required env var raises ValidationError**
    - Use `st.sampled_from(["API_URL", "SECRET_NAME", "SERVICE_NAME", "METRICS_NAMESPACE", "TABLE_NAME"])` to pick which var to omit
    - Assert `Settings()` raises `ValidationError`
    - **Validates: Requirements 5.1, 5.2**

  - [ ]* 6.9 Write property test for EventBridgeEvent camelCase round-trip (Property 8)
    - **Property 8: EventBridgeEvent camelCase round-trip**
    - Use `st.text()` for `source`/`detailType`, `st.dictionaries(st.text(), st.text())` for `detail`
    - Assert `model_dump(by_alias=True)` equals the original camelCase input dict
    - **Validates: Requirements 6.1, 6.3**

  - [ ]* 6.10 Write property test for ApiResponse camelCase round-trip (Property 9)
    - **Property 9: ApiResponse camelCase round-trip**
    - Use `st.text(min_size=1)` for `status`
    - Assert `model_dump(by_alias=True)` equals the original input dict
    - **Validates: Requirements 6.2, 6.4**

  - [ ]* 6.11 Write property test for successful response persisted to DynamoDB (Property 10)
    - **Property 10: Successful API response is persisted to DynamoDB**
    - Use `st.text(min_size=1)` for `status`; mock `secret_client`, `api_client`, and `repository`
    - Assert `repository.put_item` is called exactly once with `response.model_dump()`
    - **Validates: Requirements 11.1**

  - [ ]* 6.12 Write property test for DynamoDB write failure propagates exception (Property 11)
    - **Property 11: DynamoDB write failure propagates exception**
    - Use `st.from_type(Exception)` for exception raised by `repository.put_item`
    - Assert handler raises (does not swallow)
    - **Validates: Requirements 11.4**

  - End file with `if __name__ == "__main__": main()`
  - _Requirements: 8.1, 8.3_

- [x] 7. Checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Add documentation
  - [x] 8.1 Create `docs/template/eventbridge.md`
    - Follow the structure of `docs/template/stream.md`
    - Document: trigger (EventBridge rule), destination (external HTTP API + DynamoDB table), code locations, data models (`EventBridgeEvent`, `ApiResponse`, `Settings`), environment variables
    - _Requirements: 9.1, 9.2_

  - [x] 8.2 Update `docs/template/index.md`
    - Add a link to `eventbridge.md` alongside the existing template entries
    - _Requirements: 9.3_

- [x] 9. Update Makefile `STACK_MAP`
  - Add `STACK_MAP_eventbridge-api-caller = EventBridgeApiCallerStack` to the `STACK_MAP` variable block
  - Verify `make deploy STACK=eventbridge-api-caller` and `make destroy STACK=eventbridge-api-caller` resolve correctly
  - _Requirements: 10.1, 10.2, 10.3_

- [x] 10. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Sub-tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Property tests use Hypothesis (already a dev dependency); run with `make test`
- `ApiClient` uses `urllib.request` only — no new HTTP dependency required
- The Makefile `STACK_MAP` uses underscores in variable names; the key `eventbridge-api-caller` maps via `$(STACK_MAP_$(STACK))` substitution
- `Repository` is imported from `templates.repository` (shared class) — no new repository file is created for this scenario
