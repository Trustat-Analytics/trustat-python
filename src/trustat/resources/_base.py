"""Base classes for the resource namespaces.

Resources hold a reference to the client and turn raw envelope payloads into
typed models or pages. The sync/async split is just ``await``.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from .._models._base import TrustatModel
from ..pagination import AsyncPaginator, BasePage

if TYPE_CHECKING:
    from .._client import AsyncTrustat, Trustat

T = TypeVar("T", bound=TrustatModel)
P = TypeVar("P", bound=BasePage[Any])


class SyncResource:
    def __init__(self, client: Trustat) -> None:
        self._client = client

    def _get(self, path: str, params: Mapping[str, Any] | None, *, model: type[T]) -> T:
        payload, _ = self._client._request("GET", path, params)
        return model.model_validate(payload)

    def _get_raw(self, path: str, params: Mapping[str, Any] | None = None) -> Any:
        payload, _ = self._client._request("GET", path, params)
        return payload

    def _get_list(self, path: str, params: Mapping[str, Any] | None, *, item_key: str, model: type[T]) -> list[T]:
        payload, _ = self._client._request("GET", path, params)
        return [model.model_validate(r) for r in (payload.get(item_key) or [])]

    def _page(
        self,
        path: str,
        params: dict[str, Any],
        *,
        item_key: str,
        model: type[T],
        page_cls: type[P],
    ) -> P:
        payload, response = self._client._request("GET", path, params)
        items = [model.model_validate(r) for r in (payload.get(item_key) or [])]

        def fetch(next_params: dict[str, Any]) -> P:
            return self._page(path, next_params, item_key=item_key, model=model, page_cls=page_cls)

        return page_cls(items=items, payload=payload, params=params, response=response, fetch=fetch)


class AsyncResource:
    def __init__(self, client: AsyncTrustat) -> None:
        self._client = client

    async def _get(self, path: str, params: Mapping[str, Any] | None, *, model: type[T]) -> T:
        payload, _ = await self._client._request("GET", path, params)
        return model.model_validate(payload)

    async def _get_raw(self, path: str, params: Mapping[str, Any] | None = None) -> Any:
        payload, _ = await self._client._request("GET", path, params)
        return payload

    async def _get_list(self, path: str, params: Mapping[str, Any] | None, *, item_key: str, model: type[T]) -> list[T]:
        payload, _ = await self._client._request("GET", path, params)
        return [model.model_validate(r) for r in (payload.get(item_key) or [])]

    def _page(
        self,
        path: str,
        params: dict[str, Any],
        *,
        item_key: str,
        model: type[T],
        page_cls: type[P],
    ) -> AsyncPaginator[T]:
        """Return a lazy paginator (awaitable -> first page; async-iterable -> items)."""

        async def fetch(p: dict[str, Any]) -> P:
            payload, response = await self._client._request("GET", path, p)
            items = [model.model_validate(r) for r in (payload.get(item_key) or [])]
            return page_cls(items=items, payload=payload, params=p, response=response, fetch=fetch)

        return AsyncPaginator(fetch=fetch, params=params)
