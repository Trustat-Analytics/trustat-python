"""Tunable defaults for the Trustat client. All overridable per-client/per-call."""

from __future__ import annotations

import httpx

# Public API origin (the version prefix /public/v1 lives in the resource paths so
# root endpoints like /health and /version remain reachable from the same base).
DEFAULT_BASE_URL = "https://api-public.trustat.me"

# Split timeout: fail fast on a dead host (connect) but allow slow exports (read).
DEFAULT_TIMEOUT = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0)

# One long-lived pooled client per SDK instance; amortizes TLS across a page loop.
DEFAULT_LIMITS = httpx.Limits(max_connections=100, max_keepalive_connections=20)

# Retry policy (all Trustat ops are idempotent GETs, so retrying is always safe).
DEFAULT_MAX_RETRIES = 2
INITIAL_RETRY_DELAY = 0.5  # seconds
MAX_RETRY_DELAY = 8.0  # exponential backoff cap (before honoring server timing)
MAX_RETRY_AFTER = 60.0  # cap a server-provided Retry-After / RateLimit-Reset

# Environment fallbacks (kwarg wins, then env, then error/default).
ENV_API_KEY = "TRUSTAT_API_KEY"
ENV_BASE_URL = "TRUSTAT_BASE_URL"

# Status codes worth retrying (plus connection/timeout errors handled separately).
RETRY_STATUS_CODES = frozenset({408, 409, 429, 500, 502, 503, 504})
