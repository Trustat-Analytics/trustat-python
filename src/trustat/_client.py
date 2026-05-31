"""The sync ``Trustat`` and async ``AsyncTrustat`` clients.

Both share config/auth/URL building from ``BaseClient``; only the request loop
(sync ``time.sleep`` + ``httpx.Client`` vs async ``asyncio.sleep`` +
``httpx.AsyncClient``) and lifecycle differ.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Mapping
from typing import Any

import httpx

from ._base_client import BaseClient
from ._constants import DEFAULT_LIMITS, DEFAULT_MAX_RETRIES
from ._envelope import parse_envelope
from ._retry import retry_delay, should_retry_status
from .errors import APIConnectionError, APITimeoutError
from .resources import (
    AdsResource,
    AsyncAdsResource,
    AsyncChannelsResource,
    AsyncDictionariesResource,
    AsyncLookupResource,
    AsyncPostsResource,
    AsyncSystemResource,
    AsyncUsageResource,
    ChannelsResource,
    DictionariesResource,
    LookupResource,
    PostsResource,
    SystemResource,
    UsageResource,
)


class Trustat(BaseClient):
    """Synchronous Trustat API client.

    >>> from trustat import Trustat
    >>> with Trustat(api_key="tk_...") as client:
    ...     channel = client.channels.get("durov")
    ...     print(channel.participants)
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        auth_header: str = "authorization",
        timeout: httpx.Timeout | float | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, Any] | None = None,
        http_client: httpx.Client | None = None,
        send_telemetry: bool = True,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            auth_header=auth_header,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            send_telemetry=send_telemetry,
        )
        self._owns_http = http_client is None
        self._http = http_client or httpx.Client(timeout=self.timeout, limits=DEFAULT_LIMITS)

        self.channels = ChannelsResource(self)
        self.posts = PostsResource(self)
        self.ads = AdsResource(self)
        self.lookup = LookupResource(self)
        self.dictionaries = DictionariesResource(self)
        self.usage = UsageResource(self)
        self.system = SystemResource(self)

    def _request(self, method: str, path: str, params: Mapping[str, Any] | None = None) -> tuple[Any, httpx.Response]:
        url, query = self._prepare(path, params)
        for attempt in range(self.max_retries + 1):
            try:
                response = self._http.request(method, url, params=query, headers=self._default_headers)
            except httpx.TimeoutException as exc:
                if attempt < self.max_retries:
                    time.sleep(retry_delay(attempt))
                    continue
                raise APITimeoutError() from exc
            except httpx.HTTPError as exc:
                if attempt < self.max_retries:
                    time.sleep(retry_delay(attempt))
                    continue
                raise APIConnectionError(str(exc)) from exc
            if should_retry_status(response.status_code) and attempt < self.max_retries:
                time.sleep(retry_delay(attempt, response.headers))
                continue
            return parse_envelope(response), response
        raise APIConnectionError("Exhausted retries without a response.")  # pragma: no cover

    def close(self) -> None:
        if self._owns_http:
            self._http.close()

    def __enter__(self) -> Trustat:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


class AsyncTrustat(BaseClient):
    """Asynchronous Trustat API client.

    >>> from trustat import AsyncTrustat
    >>> async with AsyncTrustat(api_key="tk_...") as client:
    ...     channel = await client.channels.get("durov")
    ...     async for post in client.channels.posts("durov"):
    ...         ...
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        auth_header: str = "authorization",
        timeout: httpx.Timeout | float | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, Any] | None = None,
        http_client: httpx.AsyncClient | None = None,
        send_telemetry: bool = True,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            auth_header=auth_header,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            send_telemetry=send_telemetry,
        )
        self._owns_http = http_client is None
        self._http = http_client or httpx.AsyncClient(timeout=self.timeout, limits=DEFAULT_LIMITS)

        self.channels = AsyncChannelsResource(self)
        self.posts = AsyncPostsResource(self)
        self.ads = AsyncAdsResource(self)
        self.lookup = AsyncLookupResource(self)
        self.dictionaries = AsyncDictionariesResource(self)
        self.usage = AsyncUsageResource(self)
        self.system = AsyncSystemResource(self)

    async def _request(
        self, method: str, path: str, params: Mapping[str, Any] | None = None
    ) -> tuple[Any, httpx.Response]:
        url, query = self._prepare(path, params)
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._http.request(method, url, params=query, headers=self._default_headers)
            except httpx.TimeoutException as exc:
                if attempt < self.max_retries:
                    await asyncio.sleep(retry_delay(attempt))
                    continue
                raise APITimeoutError() from exc
            except httpx.HTTPError as exc:
                if attempt < self.max_retries:
                    await asyncio.sleep(retry_delay(attempt))
                    continue
                raise APIConnectionError(str(exc)) from exc
            if should_retry_status(response.status_code) and attempt < self.max_retries:
                await asyncio.sleep(retry_delay(attempt, response.headers))
                continue
            return parse_envelope(response), response
        raise APIConnectionError("Exhausted retries without a response.")  # pragma: no cover

    async def close(self) -> None:
        if self._owns_http:
            await self._http.aclose()

    async def __aenter__(self) -> AsyncTrustat:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()
