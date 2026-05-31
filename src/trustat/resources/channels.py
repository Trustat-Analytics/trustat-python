"""The ``channels`` namespace: profiles, stats, dynamics, mentions, forwards,
posts, ads, catalog and search."""

from __future__ import annotations

from typing import Any, Iterable

from .._models.models import (
    AdSummary,
    ChannelBatch,
    ChannelInfo,
    ChannelStat,
    Forward,
    Mention,
    PostSummary,
    SubscribersSeries,
    ViewsSeries,
)
from .._utils import quote_path
from ..pagination import (
    AsyncCursorPage,
    AsyncOffsetPage,
    AsyncPaginator,
    SyncCursorPage,
    SyncOffsetPage,
)
from ..types import (
    AdFormat,
    AdSort,
    AdvertiserType,
    ChannelSort,
    DateField,
    Group,
    Order,
    PeerType,
    Source,
)
from ._base import AsyncResource, SyncResource


def _catalog_params(
    *,
    source: Source,
    country: str | None,
    language: str | None,
    category_ids: Iterable[int] | str | None,
    subscribers_from: int | None,
    subscribers_to: int | None,
    avg_post_reach_from: int | None,
    avg_post_reach_to: int | None,
    avg_post_reach_24h_from: int | None,
    avg_post_reach_24h_to: int | None,
    verified: bool | None,
    peer_type: PeerType,
    sort_by: ChannelSort,
    order: Order,
    limit: int,
    cursor: str | None,
) -> dict[str, Any]:
    return {
        "source": source,
        "country": country,
        "language": language,
        "category_ids": category_ids,
        "subscribers_from": subscribers_from,
        "subscribers_to": subscribers_to,
        "avg_post_reach_from": avg_post_reach_from,
        "avg_post_reach_to": avg_post_reach_to,
        "avg_post_reach_24h_from": avg_post_reach_24h_from,
        "avg_post_reach_24h_to": avg_post_reach_24h_to,
        "verified": verified,
        "peer_type": peer_type,
        "sort_by": sort_by,
        "order": order,
        "limit": limit,
        "cursor": cursor,
    }


def _search_params(
    *,
    q: str,
    source: Source,
    country: str | None,
    language: str | None,
    category_ids: Iterable[int] | str | None,
    subscribers_from: int | None,
    subscribers_to: int | None,
    verified: bool | None,
    peer_type: PeerType,
    sort_by: ChannelSort,
    order: Order,
    limit: int,
    cursor: str | None,
) -> dict[str, Any]:
    return {
        "q": q, "source": source, "country": country, "language": language,
        "category_ids": category_ids, "subscribers_from": subscribers_from,
        "subscribers_to": subscribers_to, "verified": verified, "peer_type": peer_type,
        "sort_by": sort_by, "order": order, "limit": limit, "cursor": cursor,
    }


def _ads_params(
    *,
    ad_format: AdFormat | None,
    advertiser_type: AdvertiserType | None,
    creative_lang: str | None,
    button_text: str | None,
    color_id: int | None,
    from_date: str | None,
    to_date: str | None,
    date_field: DateField,
    sort: AdSort,
    order: Order,
    limit: int,
    cursor: str | None,
    source: Source | None,
) -> dict[str, Any]:
    return {
        "ad_format": ad_format, "advertiser_type": advertiser_type, "creative_lang": creative_lang,
        "button_text": button_text, "color_id": color_id, "from_date": from_date, "to_date": to_date,
        "date_field": date_field, "sort": sort, "order": order, "limit": limit, "cursor": cursor, "source": source,
    }


class ChannelsResource(SyncResource):
    def get(self, channel: str, *, source: Source | None = None) -> ChannelInfo:
        """Channel profile by id / ``username`` / ``@username`` / ``+hash``."""
        return self._get(f"/public/v1/channels/{quote_path(channel)}", {"source": source}, model=ChannelInfo)

    def stat(self, channel: str, *, source: Source | None = None) -> ChannelStat:
        """Channel statistics (participants, reach, ER, quality score)."""
        return self._get(f"/public/v1/channels/{quote_path(channel)}/stat", {"source": source}, model=ChannelStat)

    def batch(self, ids: Iterable[int] | str, *, source: Source = "telegram") -> ChannelBatch:
        """Fetch up to 100 channels by id in one call."""
        ids_param = ids if isinstance(ids, str) else ",".join(str(i) for i in ids)
        return self._get("/public/v1/channels/batch", {"ids": ids_param, "source": source}, model=ChannelBatch)

    def subscribers(
        self, channel: str, *, days: int = 30, from_date: str | None = None,
        to_date: str | None = None, group: Group = "day", source: Source | None = None,
    ) -> SubscribersSeries:
        """Subscriber-count time series."""
        return self._get(
            f"/public/v1/channels/{quote_path(channel)}/subscribers",
            {"days": days, "from_date": from_date, "to_date": to_date, "group": group, "source": source},
            model=SubscribersSeries,
        )

    def views(
        self, channel: str, *, days: int = 30, from_date: str | None = None,
        to_date: str | None = None, group: Group = "day", source: Source | None = None,
    ) -> ViewsSeries:
        """Average 24h-views time series."""
        return self._get(
            f"/public/v1/channels/{quote_path(channel)}/views",
            {"days": days, "from_date": from_date, "to_date": to_date, "group": group, "source": source},
            model=ViewsSeries,
        )

    def reach(
        self, channel: str, *, days: int = 30, from_date: str | None = None,
        to_date: str | None = None, group: Group = "day", source: Source | None = None,
    ) -> ViewsSeries:
        """Average 48h-reach time series."""
        return self._get(
            f"/public/v1/channels/{quote_path(channel)}/reach",
            {"days": days, "from_date": from_date, "to_date": to_date, "group": group, "source": source},
            model=ViewsSeries,
        )

    def catalog(
        self, *, source: Source = "telegram", country: str | None = None, language: str | None = None,
        category_ids: Iterable[int] | str | None = None, subscribers_from: int | None = None,
        subscribers_to: int | None = None, avg_post_reach_from: int | None = None,
        avg_post_reach_to: int | None = None, avg_post_reach_24h_from: int | None = None,
        avg_post_reach_24h_to: int | None = None, verified: bool | None = None,
        peer_type: PeerType = "channel", sort_by: ChannelSort = "subscribers",
        order: Order = "desc", limit: int = 20, cursor: str | None = None,
    ) -> SyncCursorPage[ChannelInfo]:
        """Browse the ranked channel catalog (auto-paginating)."""
        params = _catalog_params(
            source=source, country=country, language=language, category_ids=category_ids,
            subscribers_from=subscribers_from, subscribers_to=subscribers_to,
            avg_post_reach_from=avg_post_reach_from, avg_post_reach_to=avg_post_reach_to,
            avg_post_reach_24h_from=avg_post_reach_24h_from, avg_post_reach_24h_to=avg_post_reach_24h_to,
            verified=verified, peer_type=peer_type, sort_by=sort_by, order=order, limit=limit, cursor=cursor,
        )
        return self._page("/public/v1/channels/catalog", params, item_key="channels", model=ChannelInfo, page_cls=SyncCursorPage)

    def search(
        self, q: str, *, source: Source = "telegram", country: str | None = None, language: str | None = None,
        category_ids: Iterable[int] | str | None = None, subscribers_from: int | None = None,
        subscribers_to: int | None = None, verified: bool | None = None, peer_type: PeerType = "channel",
        sort_by: ChannelSort = "subscribers", order: Order = "desc", limit: int = 20, cursor: str | None = None,
    ) -> SyncCursorPage[ChannelInfo]:
        """Full-text channel search (auto-paginating)."""
        params = _search_params(
            q=q, source=source, country=country, language=language, category_ids=category_ids,
            subscribers_from=subscribers_from, subscribers_to=subscribers_to, verified=verified,
            peer_type=peer_type, sort_by=sort_by, order=order, limit=limit, cursor=cursor,
        )
        return self._page("/public/v1/channels/search", params, item_key="channels", model=ChannelInfo, page_cls=SyncCursorPage)

    def mentions(
        self, channel: str, *, from_date: str | None = None, to_date: str | None = None,
        limit: int = 20, offset: int = 0, source: Source | None = None,
    ) -> SyncOffsetPage[Mention]:
        """Who mentioned this channel (auto-paginating; depth-capped ~10k)."""
        params = {"from_date": from_date, "to_date": to_date, "limit": limit, "offset": offset, "source": source}
        return self._page(f"/public/v1/channels/{quote_path(channel)}/mentions", params, item_key="mentions", model=Mention, page_cls=SyncOffsetPage)

    def forwards(
        self, channel: str, *, from_date: str | None = None, to_date: str | None = None,
        peer_type: PeerType = "channel", limit: int = 20, offset: int = 0, source: Source | None = None,
    ) -> SyncOffsetPage[Forward]:
        """Channels that forwarded this channel's posts (auto-paginating; depth-capped ~10k)."""
        params = {"from_date": from_date, "to_date": to_date, "peer_type": peer_type, "limit": limit, "offset": offset, "source": source}
        return self._page(f"/public/v1/channels/{quote_path(channel)}/forwards", params, item_key="forwards", model=Forward, page_cls=SyncOffsetPage)

    def posts(
        self, channel: str, *, from_date: str | None = None, to_date: str | None = None,
        hide_forwards: bool = False, hide_deleted: bool = True, limit: int = 20,
        cursor: str | None = None, source: Source | None = None,
    ) -> SyncCursorPage[PostSummary]:
        """The channel's post feed (auto-paginating)."""
        params = {
            "from_date": from_date, "to_date": to_date, "hide_forwards": hide_forwards,
            "hide_deleted": hide_deleted, "limit": limit, "cursor": cursor, "source": source,
        }
        return self._page(f"/public/v1/channels/{quote_path(channel)}/posts", params, item_key="posts", model=PostSummary, page_cls=SyncCursorPage)

    def ads(
        self, channel: str, *, ad_format: AdFormat | None = None, advertiser_type: AdvertiserType | None = None,
        creative_lang: str | None = None, button_text: str | None = None, color_id: int | None = None,
        from_date: str | None = None, to_date: str | None = None, date_field: DateField = "last_seen",
        sort: AdSort = "last_seen", order: Order = "desc", limit: int = 20, cursor: str | None = None,
        source: Source | None = None,
    ) -> SyncCursorPage[AdSummary]:
        """Telegram Ads that ran in this channel (auto-paginating)."""
        params = _ads_params(
            ad_format=ad_format, advertiser_type=advertiser_type, creative_lang=creative_lang,
            button_text=button_text, color_id=color_id, from_date=from_date, to_date=to_date,
            date_field=date_field, sort=sort, order=order, limit=limit, cursor=cursor, source=source,
        )
        return self._page(f"/public/v1/channels/{quote_path(channel)}/ads", params, item_key="ads", model=AdSummary, page_cls=SyncCursorPage)


class AsyncChannelsResource(AsyncResource):
    async def get(self, channel: str, *, source: Source | None = None) -> ChannelInfo:
        """Channel profile by id / ``username`` / ``@username`` / ``+hash``."""
        return await self._get(f"/public/v1/channels/{quote_path(channel)}", {"source": source}, model=ChannelInfo)

    async def stat(self, channel: str, *, source: Source | None = None) -> ChannelStat:
        """Channel statistics (participants, reach, ER, quality score)."""
        return await self._get(f"/public/v1/channels/{quote_path(channel)}/stat", {"source": source}, model=ChannelStat)

    async def batch(self, ids: Iterable[int] | str, *, source: Source = "telegram") -> ChannelBatch:
        """Fetch up to 100 channels by id in one call."""
        ids_param = ids if isinstance(ids, str) else ",".join(str(i) for i in ids)
        return await self._get("/public/v1/channels/batch", {"ids": ids_param, "source": source}, model=ChannelBatch)

    async def subscribers(
        self, channel: str, *, days: int = 30, from_date: str | None = None,
        to_date: str | None = None, group: Group = "day", source: Source | None = None,
    ) -> SubscribersSeries:
        """Subscriber-count time series."""
        return await self._get(
            f"/public/v1/channels/{quote_path(channel)}/subscribers",
            {"days": days, "from_date": from_date, "to_date": to_date, "group": group, "source": source},
            model=SubscribersSeries,
        )

    async def views(
        self, channel: str, *, days: int = 30, from_date: str | None = None,
        to_date: str | None = None, group: Group = "day", source: Source | None = None,
    ) -> ViewsSeries:
        """Average 24h-views time series."""
        return await self._get(
            f"/public/v1/channels/{quote_path(channel)}/views",
            {"days": days, "from_date": from_date, "to_date": to_date, "group": group, "source": source},
            model=ViewsSeries,
        )

    async def reach(
        self, channel: str, *, days: int = 30, from_date: str | None = None,
        to_date: str | None = None, group: Group = "day", source: Source | None = None,
    ) -> ViewsSeries:
        """Average 48h-reach time series."""
        return await self._get(
            f"/public/v1/channels/{quote_path(channel)}/reach",
            {"days": days, "from_date": from_date, "to_date": to_date, "group": group, "source": source},
            model=ViewsSeries,
        )

    def catalog(
        self, *, source: Source = "telegram", country: str | None = None, language: str | None = None,
        category_ids: Iterable[int] | str | None = None, subscribers_from: int | None = None,
        subscribers_to: int | None = None, avg_post_reach_from: int | None = None,
        avg_post_reach_to: int | None = None, avg_post_reach_24h_from: int | None = None,
        avg_post_reach_24h_to: int | None = None, verified: bool | None = None,
        peer_type: PeerType = "channel", sort_by: ChannelSort = "subscribers",
        order: Order = "desc", limit: int = 20, cursor: str | None = None,
    ) -> AsyncPaginator[ChannelInfo]:
        """Browse the ranked channel catalog (auto-paginating)."""
        params = _catalog_params(
            source=source, country=country, language=language, category_ids=category_ids,
            subscribers_from=subscribers_from, subscribers_to=subscribers_to,
            avg_post_reach_from=avg_post_reach_from, avg_post_reach_to=avg_post_reach_to,
            avg_post_reach_24h_from=avg_post_reach_24h_from, avg_post_reach_24h_to=avg_post_reach_24h_to,
            verified=verified, peer_type=peer_type, sort_by=sort_by, order=order, limit=limit, cursor=cursor,
        )
        return self._page("/public/v1/channels/catalog", params, item_key="channels", model=ChannelInfo, page_cls=AsyncCursorPage)

    def search(
        self, q: str, *, source: Source = "telegram", country: str | None = None, language: str | None = None,
        category_ids: Iterable[int] | str | None = None, subscribers_from: int | None = None,
        subscribers_to: int | None = None, verified: bool | None = None, peer_type: PeerType = "channel",
        sort_by: ChannelSort = "subscribers", order: Order = "desc", limit: int = 20, cursor: str | None = None,
    ) -> AsyncPaginator[ChannelInfo]:
        """Full-text channel search (auto-paginating)."""
        params = _search_params(
            q=q, source=source, country=country, language=language, category_ids=category_ids,
            subscribers_from=subscribers_from, subscribers_to=subscribers_to, verified=verified,
            peer_type=peer_type, sort_by=sort_by, order=order, limit=limit, cursor=cursor,
        )
        return self._page("/public/v1/channels/search", params, item_key="channels", model=ChannelInfo, page_cls=AsyncCursorPage)

    def mentions(
        self, channel: str, *, from_date: str | None = None, to_date: str | None = None,
        limit: int = 20, offset: int = 0, source: Source | None = None,
    ) -> AsyncPaginator[Mention]:
        """Who mentioned this channel (auto-paginating; depth-capped ~10k)."""
        params = {"from_date": from_date, "to_date": to_date, "limit": limit, "offset": offset, "source": source}
        return self._page(f"/public/v1/channels/{quote_path(channel)}/mentions", params, item_key="mentions", model=Mention, page_cls=AsyncOffsetPage)

    def forwards(
        self, channel: str, *, from_date: str | None = None, to_date: str | None = None,
        peer_type: PeerType = "channel", limit: int = 20, offset: int = 0, source: Source | None = None,
    ) -> AsyncPaginator[Forward]:
        """Channels that forwarded this channel's posts (auto-paginating; depth-capped ~10k)."""
        params = {"from_date": from_date, "to_date": to_date, "peer_type": peer_type, "limit": limit, "offset": offset, "source": source}
        return self._page(f"/public/v1/channels/{quote_path(channel)}/forwards", params, item_key="forwards", model=Forward, page_cls=AsyncOffsetPage)

    def posts(
        self, channel: str, *, from_date: str | None = None, to_date: str | None = None,
        hide_forwards: bool = False, hide_deleted: bool = True, limit: int = 20,
        cursor: str | None = None, source: Source | None = None,
    ) -> AsyncPaginator[PostSummary]:
        """The channel's post feed (auto-paginating)."""
        params = {
            "from_date": from_date, "to_date": to_date, "hide_forwards": hide_forwards,
            "hide_deleted": hide_deleted, "limit": limit, "cursor": cursor, "source": source,
        }
        return self._page(f"/public/v1/channels/{quote_path(channel)}/posts", params, item_key="posts", model=PostSummary, page_cls=AsyncCursorPage)

    def ads(
        self, channel: str, *, ad_format: AdFormat | None = None, advertiser_type: AdvertiserType | None = None,
        creative_lang: str | None = None, button_text: str | None = None, color_id: int | None = None,
        from_date: str | None = None, to_date: str | None = None, date_field: DateField = "last_seen",
        sort: AdSort = "last_seen", order: Order = "desc", limit: int = 20, cursor: str | None = None,
        source: Source | None = None,
    ) -> AsyncPaginator[AdSummary]:
        """Telegram Ads that ran in this channel (auto-paginating)."""
        params = _ads_params(
            ad_format=ad_format, advertiser_type=advertiser_type, creative_lang=creative_lang,
            button_text=button_text, color_id=color_id, from_date=from_date, to_date=to_date,
            date_field=date_field, sort=sort, order=order, limit=limit, cursor=cursor, source=source,
        )
        return self._page(f"/public/v1/channels/{quote_path(channel)}/ads", params, item_key="ads", model=AdSummary, page_cls=AsyncCursorPage)
