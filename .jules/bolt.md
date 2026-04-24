## 2024-04-24 - [Pydantic V2 Native JSON Performance]
**Learning:** Pydantic V2 uses a Rust-based JSON parser (jiter). Using `model_validate_json()` and `model_dump_json()` is significantly faster (50-60%) than the traditional `json.loads/dumps` with `model_validate/dump`.
**Action:** Always prefer `model_validate_json()` when handling raw JSON strings in Lambda handlers to reduce cold start impact and execution time.
