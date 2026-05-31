"""Typed views over the API's rate-limit and quota response headers.

Surfaced on every page/response so callers can self-throttle and watch quota
burn-down without poking at raw headers.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


def _to_int(value: str | None) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _to_float(value: str | None) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _first(headers: Mapping[str, str], *names: str) -> str | None:
    # httpx.Headers is case-insensitive; support both the IETF RateLimit-* and the
    # legacy X-RateLimit-* spellings.
    for name in names:
        try:
            value = headers.get(name)
        except Exception:
            value = None
        if value is not None:
            return value
    return None


def _split_pair(value: str | None) -> tuple[int, int] | None:
    """Parse a ``"used/limit"`` quota header into a (used, limit) tuple."""
    if not value or "/" not in value:
        return None
    used, _, limit = value.partition("/")
    u, lim = _to_int(used.strip()), _to_int(limit.strip())
    return (u, lim) if u is not None and lim is not None else None


@dataclass(frozen=True)
class RateLimit:
    """Token-bucket rate-limit state from ``RateLimit-*`` headers."""

    limit: int | None = None
    remaining: int | None = None
    reset_seconds: float | None = None
    reset_at: datetime | None = None

    @classmethod
    def from_headers(cls, headers: Mapping[str, str]) -> RateLimit:
        reset_s = _to_float(_first(headers, "ratelimit-reset", "x-ratelimit-reset"))
        reset_at = datetime.now(timezone.utc) + timedelta(seconds=reset_s) if reset_s is not None else None
        return cls(
            limit=_to_int(_first(headers, "ratelimit-limit", "x-ratelimit-limit")),
            remaining=_to_int(_first(headers, "ratelimit-remaining", "x-ratelimit-remaining")),
            reset_seconds=reset_s,
            reset_at=reset_at,
        )


@dataclass(frozen=True)
class Quota:
    """Monthly quota state from ``X-Quota-*`` headers, each as (used, limit)."""

    requests: tuple[int, int] | None = None
    channels: tuple[int, int] | None = None
    listing: tuple[int, int] | None = None
    overage: bool = False

    @classmethod
    def from_headers(cls, headers: Mapping[str, str]) -> Quota:
        return cls(
            requests=_split_pair(_first(headers, "x-quota-requests")),
            channels=_split_pair(_first(headers, "x-quota-channels")),
            listing=_split_pair(_first(headers, "x-quota-listing")),
            overage=(_first(headers, "x-quota-overage") or "").lower() == "true",
        )

    @property
    def requests_remaining(self) -> int | None:
        if self.requests is None:
            return None
        used, limit = self.requests
        return max(0, limit - used) if limit else None
