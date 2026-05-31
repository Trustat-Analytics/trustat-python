"""The ``posts`` namespace: search, single post, edit history, stats."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .._models.models import Post, PostHistory, PostStat, PostSummary
from .._utils import quote_path
from ..pagination import AsyncCursorPage, AsyncPaginator, SyncCursorPage
from ..types import Order, PeerType, PostSort, Source
from ._base import AsyncResource, SyncResource


def _search_params(
    *,
    q: str | None,
    source: Source,
    channel_id: int | None,
    since_ts: int | None,
    until_ts: int | None,
    views_min: int | None,
    minus_words: Iterable[str] | str | None,
    hide_forwards: bool,
    hide_deleted: bool,
    peer_type: PeerType,
    sort: PostSort,
    order: Order,
    limit: int,
    cursor: str | None,
) -> dict[str, Any]:
    return {
        "q": q,
        "source": source,
        "channel_id": channel_id,
        "since_ts": since_ts,
        "until_ts": until_ts,
        "views_min": views_min,
        "minus_words": minus_words,
        "hide_forwards": hide_forwards,
        "hide_deleted": hide_deleted,
        "peer_type": peer_type,
        "sort": sort,
        "order": order,
        "limit": limit,
        "cursor": cursor,
    }


class PostsResource(SyncResource):
    def search(
        self,
        q: str | None = None,
        *,
        source: Source = "telegram",
        channel_id: int | None = None,
        since_ts: int | None = None,
        until_ts: int | None = None,
        views_min: int | None = None,
        minus_words: Iterable[str] | str | None = None,
        hide_forwards: bool = False,
        hide_deleted: bool = True,
        peer_type: PeerType = "channel",
        sort: PostSort = "date",
        order: Order = "desc",
        limit: int = 20,
        cursor: str | None = None,
    ) -> SyncCursorPage[PostSummary]:
        """Global post search (auto-paginating). Provide ``q`` and/or ``channel_id``."""
        params = _search_params(
            q=q,
            source=source,
            channel_id=channel_id,
            since_ts=since_ts,
            until_ts=until_ts,
            views_min=views_min,
            minus_words=minus_words,
            hide_forwards=hide_forwards,
            hide_deleted=hide_deleted,
            peer_type=peer_type,
            sort=sort,
            order=order,
            limit=limit,
            cursor=cursor,
        )
        return self._page(
            "/public/v1/posts/search", params, item_key="posts", model=PostSummary, page_cls=SyncCursorPage
        )

    def get(self, post_id: str, *, source: Source | None = None) -> Post:
        """A single post by ``<channel_id>_<message_id>`` or a t.me/max.ru post link."""
        return self._get(f"/public/v1/posts/{quote_path(post_id)}", {"source": source}, model=Post)

    def history(self, post_id: str, *, source: Source | None = None) -> PostHistory:
        """The edit history (all stored versions) of a post."""
        return self._get(f"/public/v1/posts/{quote_path(post_id)}/history", {"source": source}, model=PostHistory)

    def stat(self, post_id: str, *, source: Source | None = None) -> PostStat:
        """Latest stats (views, forwards, reactions) for a post."""
        return self._get(f"/public/v1/posts/{quote_path(post_id)}/stat", {"source": source}, model=PostStat)


class AsyncPostsResource(AsyncResource):
    def search(
        self,
        q: str | None = None,
        *,
        source: Source = "telegram",
        channel_id: int | None = None,
        since_ts: int | None = None,
        until_ts: int | None = None,
        views_min: int | None = None,
        minus_words: Iterable[str] | str | None = None,
        hide_forwards: bool = False,
        hide_deleted: bool = True,
        peer_type: PeerType = "channel",
        sort: PostSort = "date",
        order: Order = "desc",
        limit: int = 20,
        cursor: str | None = None,
    ) -> AsyncPaginator[PostSummary]:
        """Global post search (auto-paginating). Provide ``q`` and/or ``channel_id``."""
        params = _search_params(
            q=q,
            source=source,
            channel_id=channel_id,
            since_ts=since_ts,
            until_ts=until_ts,
            views_min=views_min,
            minus_words=minus_words,
            hide_forwards=hide_forwards,
            hide_deleted=hide_deleted,
            peer_type=peer_type,
            sort=sort,
            order=order,
            limit=limit,
            cursor=cursor,
        )
        return self._page(
            "/public/v1/posts/search", params, item_key="posts", model=PostSummary, page_cls=AsyncCursorPage
        )

    async def get(self, post_id: str, *, source: Source | None = None) -> Post:
        """A single post by ``<channel_id>_<message_id>`` or a t.me/max.ru post link."""
        return await self._get(f"/public/v1/posts/{quote_path(post_id)}", {"source": source}, model=Post)

    async def history(self, post_id: str, *, source: Source | None = None) -> PostHistory:
        """The edit history (all stored versions) of a post."""
        return await self._get(f"/public/v1/posts/{quote_path(post_id)}/history", {"source": source}, model=PostHistory)

    async def stat(self, post_id: str, *, source: Source | None = None) -> PostStat:
        """Latest stats (views, forwards, reactions) for a post."""
        return await self._get(f"/public/v1/posts/{quote_path(post_id)}/stat", {"source": source}, model=PostStat)
