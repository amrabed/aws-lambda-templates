## 2025-05-15 - [EventBridge] High-Performance JSON Parsing with model_validate_json
**Learning:** For external API responses, Pydantic's `model_validate_json(response.content)` is significantly faster than `model_validate(response.json())`. This is because `model_validate_json` leverages Pydantic's high-performance Rust-based JSON parser directly on raw bytes, bypassing the intermediate Python dictionary creation by `response.json()`.
**Action:** Use `model_validate_json` when processing raw JSON payloads from external HTTP calls or events to minimize Lambda execution time.

## 2025-05-15 - [EventBridge] Connection Pooling with requests.Session
**Learning:** Reusing a `requests.Session` in AWS Lambda allows for TCP/TLS connection pooling across warm starts. This can reduce latency by 50-200ms per request by avoiding the overhead of establishing a new connection for every invocation.
**Action:** Always instantiate `requests.Session()` at the class level or module level for persistent outbound HTTP connections.

## 2025-05-15 - [GraphQL] Rejected: TypeAdapter for List Validation
**Learning:** While `pydantic.TypeAdapter(list[Model])` provides a theoretical ~65% performance improvement over list comprehensions by leveraging Rust-based batch processing, it may be rejected if the perceived value is low relative to the original implementation's simplicity, especially in template code.
**Action:** Prioritize optimizations that have a dramatic and undeniable impact on core latency or resource consumption.

## 2026-06-10 - [Stream] Faster Cross-Model Validation with from_attributes
**Learning:** When validating a Pydantic model using data from another Pydantic model (e.g., transforming a `SourceItem` to a `DestinationItem`), using `Model.model_validate(other_model, from_attributes=True)` is significantly faster and more memory-efficient than `Model.model_validate(other_model.model_dump())`. It bypasses the overhead of serializing the source model into an intermediate Python dictionary.
**Action:** Use `from_attributes=True` for efficient model-to-model transformations, especially in high-throughput data processing paths like DynamoDB Streams or SQS batch processing.
