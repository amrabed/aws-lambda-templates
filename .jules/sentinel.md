## 2025-05-22 - [Sensitive Data Exposure in API Responses]
**Vulnerability:** API handlers returning raw database records (dicts) directly to clients.
**Learning:** Returning raw database items bypasses Pydantic model filtering, potentially exposing internal or sensitive fields (e.g., `secret_note`, `internal_id`) that exist in the database but are not defined in the public model.
**Prevention:** Always validate database records against a Pydantic model and use `model_dump()` (or a helper like `dump()`) to ensure only allowed fields are serialized in the response.
