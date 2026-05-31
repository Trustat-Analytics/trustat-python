"""Retry decision + backoff timing.

All Trustat operations are idempotent GETs, so retrying is always safe. We retry
transient statuses (408/409/429/5xx) and connection/timeout errors, with
exponential backoff + jitter, but prefer server-provided timing (Retry-After /
RateLimit-Reset) when present, capped so a hostile header can't park the client.
"""

from __future__ import annotations

import email.utils
import random
from datetime import datetime, timezone
from typing import Mapping

from ._constants import INITIAL_RETRY_DELAY, MAX_RETRY_AFTER, MAX_RETRY_DELAY, RETRY_STATUS_CODES


def should_retry_status(status_code: int) -> bool:
    return status_code in RETRY_STATUS_CODES


def parse_retry_after(headers: Mapping[str, str]) -> float | None:
    """Seconds to wait per the server, from Retry-After (secs or HTTP-date) or
    RateLimit-Reset. Returns None if no usable header is present."""

    def _get(*names: str) -> str | None:
        for n in names:
            try:
                v = headers.get(n)
            except Exception:
                v = None
            if v:
                return v
        return None

    retry_after = _get("retry-after")
    if retry_after:
        try:
            return max(0.0, float(retry_after))
        except ValueError:
            try:
                when = email.utils.parsedate_to_datetime(retry_after)
                if when is not None:
                    if when.tzinfo is None:
                        when = when.replace(tzinfo=timezone.utc)
                    return max(0.0, (when - datetime.now(timezone.utc)).total_seconds())
            except (TypeError, ValueError):
                pass
    reset = _get("ratelimit-reset", "x-ratelimit-reset")
    if reset:
        try:
            return max(0.0, float(reset))
        except ValueError:
            pass
    return None


def retry_delay(attempt: int, headers: Mapping[str, str] | None = None) -> float:
    """Seconds to sleep before retry ``attempt`` (0-based).

    Honors server timing first (capped at MAX_RETRY_AFTER), else exponential
    backoff (INITIAL_RETRY_DELAY * 2**attempt, capped) with up to 25% downward
    jitter to avoid synchronized retries.
    """
    if headers is not None:
        server = parse_retry_after(headers)
        if server is not None:
            return min(server, MAX_RETRY_AFTER)
    base = min(INITIAL_RETRY_DELAY * (2.0**attempt), MAX_RETRY_DELAY)
    return base * (1.0 - 0.25 * random.random())
