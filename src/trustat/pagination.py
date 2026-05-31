"""Lazy auto-pagination.

A page is iterable: iterating it transparently fetches subsequent pages, so you
can ``for item in client.channels.search(q=...)`` over an entire result set
without managing cursors. ``.iter_pages()`` yields whole pages instead.

Two server mechanisms are supported:
  * **Cursor** (catalog, search, channel posts, ads) — follows ``next_cursor``.
  * **Offset** (mentions, forwards) — increments the page ``offset`` until a
    short page. NB: these are depth-capped server-side (~10k results); iterating
    past the cap raises ``BadRequestError`` (narrow the date range instead).

``page.total`` is the API's *approximate* total — informational only; never use
it to bound the loop (always rely on cursor/short-page).
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Iterator
from typing import Any, Generic, TypeVar, cast

import httpx

from ._rate_limit import Quota, RateLimit

T = TypeVar("T")

# A fetcher takes the next query params and returns the next page (sync or async).
SyncFetch = Callable[[dict[str, Any]], "BasePage[Any]"]
AsyncFetch = Callable[[dict[str, Any]], Any]  # returns Awaitable[BasePage]


class BasePage(Generic[T]):
    """Common state for a single page of results."""

    def __init__(
        self,
        *,
        items: list[T],
        payload: dict[str, Any],
        params: dict[str, Any],
        response: httpx.Response,
        fetch: Callable[..., Any],
    ) -> None:
        self.items: list[T] = items
        self._payload = payload
        self._params = params
        self.response = response
        self._fetch = fetch
        #: The API's approximate total match count (informational; may be capped).
        self.total: int | None = payload.get("total")
        #: Rate-limit state from this page's response headers.
        self.rate_limit = RateLimit.from_headers(response.headers)
        #: Monthly quota state from this page's response headers.
        self.quota = Quota.from_headers(response.headers)

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> T:
        return self.items[index]

    def __repr__(self) -> str:
        return f"<{type(self).__name__} items={len(self.items)} total~{self.total} has_next={self.has_next_page()}>"

    # --- subclass hooks ---
    def has_next_page(self) -> bool:  # pragma: no cover - overridden
        raise NotImplementedError

    def _next_params(self) -> dict[str, Any]:  # pragma: no cover - overridden
        raise NotImplementedError


class _CursorMixin:
    def has_next_page(self) -> bool:
        return bool(self._payload.get("next_cursor"))  # type: ignore[attr-defined]

    def _next_params(self) -> dict[str, Any]:
        return {**self._params, "cursor": self._payload.get("next_cursor")}  # type: ignore[attr-defined]

    @property
    def next_cursor(self) -> str | None:
        return cast("str | None", self._payload.get("next_cursor"))  # type: ignore[attr-defined]


class _OffsetMixin:
    def has_next_page(self) -> bool:
        limit = self._params.get("limit")  # type: ignore[attr-defined]
        if not self.items:  # type: ignore[attr-defined]
            return False
        # A full page implies there may be more; a short page is the end.
        return limit is not None and len(self.items) >= int(limit)  # type: ignore[attr-defined]

    def _next_params(self) -> dict[str, Any]:
        current = self._params.get("offset") or 0  # type: ignore[attr-defined]
        return {**self._params, "offset": int(current) + 1}  # type: ignore[attr-defined]


# --------------------------------------------------------------------------- #
# Sync pages
# --------------------------------------------------------------------------- #
class _SyncPage(BasePage[T]):
    def next_page(self) -> _SyncPage[T] | None:
        if not self.has_next_page():
            return None
        return cast("_SyncPage[T]", self._fetch(self._next_params()))

    def iter_pages(self) -> Iterator[_SyncPage[T]]:
        page: _SyncPage[T] | None = self
        while page is not None:
            yield page
            page = page.next_page()

    def __iter__(self) -> Iterator[T]:
        for page in self.iter_pages():
            yield from page.items


class SyncCursorPage(_CursorMixin, _SyncPage[T]):
    pass


class SyncOffsetPage(_OffsetMixin, _SyncPage[T]):
    pass


# --------------------------------------------------------------------------- #
# Async pages
# --------------------------------------------------------------------------- #
class _AsyncPage(BasePage[T]):
    async def next_page(self) -> _AsyncPage[T] | None:
        if not self.has_next_page():
            return None
        return cast("_AsyncPage[T]", await self._fetch(self._next_params()))

    async def iter_pages(self) -> AsyncIterator[_AsyncPage[T]]:
        page: _AsyncPage[T] | None = self
        while page is not None:
            yield page
            page = await page.next_page()

    async def __aiter__(self) -> AsyncIterator[T]:
        async for page in self.iter_pages():
            for item in page.items:
                yield item


class AsyncCursorPage(_CursorMixin, _AsyncPage[T]):
    pass


class AsyncOffsetPage(_OffsetMixin, _AsyncPage[T]):
    pass


class AsyncPaginator(Generic[T]):
    """Lazy entry point for an async listing.

    Returned (not awaited) by async list methods so it can be used either way:

        page = await client.channels.search(q="news")     # -> AsyncCursorPage
        async for ch in client.channels.search(q="news"):  # -> items, auto-paged
            ...
        async for page in client.channels.search(q="news").iter_pages():
            ...

    No I/O happens until you await or iterate.
    """

    def __init__(self, *, fetch: Callable[[dict[str, Any]], Any], params: dict[str, Any]) -> None:
        self._fetch = fetch  # async callable(params) -> _AsyncPage
        self._params = params

    def __await__(self):  # type: ignore[no-untyped-def]
        return self._fetch(self._params).__await__()

    async def __aiter__(self) -> AsyncIterator[T]:
        page: _AsyncPage[T] | None = await self._fetch(self._params)
        while page is not None:
            for item in page.items:
                yield item
            page = await page.next_page()

    async def iter_pages(self) -> AsyncIterator[_AsyncPage[T]]:
        page: _AsyncPage[T] | None = await self._fetch(self._params)
        while page is not None:
            yield page
            page = await page.next_page()
