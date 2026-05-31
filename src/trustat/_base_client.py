"""Shared configuration + request preparation for the sync and async clients.

The sync/async request *loops* live in ``_client.py`` (they differ only in
``time.sleep`` vs ``await asyncio.sleep`` and sync vs async httpx calls); all the
config resolution, auth, header, URL and query building is shared here.
"""

from __future__ import annotations

import os
from typing import Any, Mapping

import httpx

from ._constants import DEFAULT_BASE_URL, DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT, ENV_API_KEY, ENV_BASE_URL
from ._utils import redact_key, serialize_query, user_agent
from .errors import TrustatError

AuthHeader = str  # Literal["authorization", "x-api-key"] — validated below


class BaseClient:
    """Resolves config (api_key/base_url/auth/headers) shared by both clients."""

    def __init__(
        self,
        *,
        api_key: str | None,
        base_url: str | None,
        auth_header: AuthHeader,
        timeout: httpx.Timeout | float | None,
        max_retries: int,
        default_headers: Mapping[str, str] | None,
        default_query: Mapping[str, Any] | None,
        send_telemetry: bool,
    ) -> None:
        key = api_key if api_key is not None else os.environ.get(ENV_API_KEY)
        if not key:
            raise TrustatError(
                "No API key provided. Pass api_key=... or set the "
                f"{ENV_API_KEY} environment variable."
            )
        if auth_header not in ("authorization", "x-api-key"):
            raise TrustatError("auth_header must be 'authorization' or 'x-api-key'")

        self.api_key: str = key
        self.base_url: str = (
            base_url if base_url is not None else os.environ.get(ENV_BASE_URL) or DEFAULT_BASE_URL
        ).rstrip("/")
        self.max_retries: int = max(0, int(max_retries))
        self.timeout: httpx.Timeout | float = DEFAULT_TIMEOUT if timeout is None else timeout
        self._auth_header = auth_header
        self._default_query = serialize_query(default_query)
        self._default_headers = self._build_headers(send_telemetry, default_headers)

    def _build_headers(self, send_telemetry: bool, extra: Mapping[str, str] | None) -> dict[str, str]:
        headers: dict[str, str] = {"Accept": "application/json"}
        if send_telemetry:
            headers["User-Agent"] = user_agent()
        if self._auth_header == "x-api-key":
            headers["X-API-Key"] = self.api_key
        else:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if extra:
            headers.update(extra)
        return headers

    def _prepare(self, path: str, params: Mapping[str, Any] | None) -> tuple[str, dict[str, Any]]:
        """Build the absolute URL + merged query for a request.

        Absolute URLs (rather than an httpx ``base_url``) keep things working when
        a caller injects their own ``http_client`` without a base_url configured.
        """
        url = f"{self.base_url}{path}"
        query = {**self._default_query, **serialize_query(params)}
        return url, query

    def __repr__(self) -> str:
        return f"{type(self).__name__}(base_url={self.base_url!r}, api_key={redact_key(self.api_key)!r})"
