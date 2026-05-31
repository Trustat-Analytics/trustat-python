# Changelog

All notable changes to the Trustat Python SDK are documented here.
This project follows [Semantic Versioning](https://semver.org/).

## [0.1.0] — 2026-05-31

Initial release.

- Sync (`Trustat`) and async (`AsyncTrustat`) clients sharing one transport core.
- Resource namespaces: `channels`, `posts`, `ads`, `lookup`, `dictionaries`, `usage`, `system`
  — covering all 28 API endpoints.
- Typed Pydantic v2 response models (forward-compatible: unknown fields preserved,
  missing fields tolerated).
- Automatic cursor + offset pagination (lazy `for` / `async for`, plus `iter_pages()`).
- Automatic retries (429/5xx/connection) with exponential backoff + jitter, honoring
  `Retry-After` / `RateLimit-Reset`.
- Typed error hierarchy mapping the API's error codes; `request_id` surfaced on every error.
- Rate-limit and quota state surfaced on every page (`page.rate_limit`, `page.quota`).
- `Authorization: Bearer` / `X-API-Key` auth, env-var config, injectable httpx client.
- `py.typed`, `mypy --strict` clean.
