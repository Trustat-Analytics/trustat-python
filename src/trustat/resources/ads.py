"""The ``ads`` namespace: Telegram Ads search, creative card, facets, timeline,
and ads by advertiser domain."""

from __future__ import annotations

from typing import Any, Iterable

from .._models.models import AdCreative, AdFacets, AdsTimeline, AdSummary
from .._utils import quote_path
from ..pagination import AsyncCursorPage, AsyncPaginator, SyncCursorPage
from ..types import AdFormat, AdSort, AdvertiserType, DateField, Group, Order
from ._base import AsyncResource, SyncResource


def _filter_params(
    *,
    q: str | None,
    ad_format: AdFormat | None,
    advertiser_type: AdvertiserType | None,
    creative_lang: str | None,
    channel_country: str | None,
    channel_lang: str | None,
    category_ids: Iterable[int] | str | None,
    channel: str | None,
    button_text: str | None,
    color_id: int | None,
    from_date: str | None,
    to_date: str | None,
    date_field: DateField,
) -> dict[str, Any]:
    return {
        "q": q, "ad_format": ad_format, "advertiser_type": advertiser_type,
        "creative_lang": creative_lang, "channel_country": channel_country,
        "channel_lang": channel_lang, "category_ids": category_ids, "channel": channel,
        "button_text": button_text, "color_id": color_id, "from_date": from_date,
        "to_date": to_date, "date_field": date_field,
    }


class AdsResource(SyncResource):
    def search(
        self,
        q: str | None = None,
        *,
        ad_format: AdFormat | None = None,
        advertiser_type: AdvertiserType | None = None,
        creative_lang: str | None = None,
        channel_country: str | None = None,
        channel_lang: str | None = None,
        category_ids: Iterable[int] | str | None = None,
        channel: str | None = None,
        button_text: str | None = None,
        color_id: int | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        date_field: DateField = "last_seen",
        sort: AdSort = "last_seen",
        order: Order = "desc",
        limit: int = 20,
        cursor: str | None = None,
    ) -> SyncCursorPage[AdSummary]:
        """Search the Telegram Ads creatives index (auto-paginating)."""
        params = {
            **_filter_params(
                q=q, ad_format=ad_format, advertiser_type=advertiser_type, creative_lang=creative_lang,
                channel_country=channel_country, channel_lang=channel_lang, category_ids=category_ids,
                channel=channel, button_text=button_text, color_id=color_id, from_date=from_date,
                to_date=to_date, date_field=date_field,
            ),
            "sort": sort, "order": order, "limit": limit, "cursor": cursor,
        }
        return self._page("/public/v1/ads/search", params, item_key="ads", model=AdSummary, page_cls=SyncCursorPage)

    def get(self, creative_hash: str) -> AdCreative:
        """The full creative card for one ad."""
        return self._get(f"/public/v1/ads/{quote_path(creative_hash)}", None, model=AdCreative)

    def facets(
        self, q: str | None = None, *, ad_format: AdFormat | None = None,
        advertiser_type: AdvertiserType | None = None, creative_lang: str | None = None,
        channel_country: str | None = None, channel_lang: str | None = None,
        category_ids: Iterable[int] | str | None = None, channel: str | None = None,
        button_text: str | None = None, color_id: int | None = None,
        from_date: str | None = None, to_date: str | None = None, date_field: DateField = "last_seen",
    ) -> AdFacets:
        """Available filter values (facets) for the current ad query."""
        params = _filter_params(
            q=q, ad_format=ad_format, advertiser_type=advertiser_type, creative_lang=creative_lang,
            channel_country=channel_country, channel_lang=channel_lang, category_ids=category_ids,
            channel=channel, button_text=button_text, color_id=color_id, from_date=from_date,
            to_date=to_date, date_field=date_field,
        )
        return self._get("/public/v1/ads/facets", params, model=AdFacets)

    def timeline(
        self, q: str | None = None, *, group: Group = "month", ad_format: AdFormat | None = None,
        advertiser_type: AdvertiserType | None = None, creative_lang: str | None = None,
        channel_country: str | None = None, channel_lang: str | None = None,
        category_ids: Iterable[int] | str | None = None, channel: str | None = None,
        button_text: str | None = None, color_id: int | None = None,
        from_date: str | None = None, to_date: str | None = None, date_field: DateField = "last_seen",
    ) -> AdsTimeline:
        """Ad-volume time series for the current query."""
        params = {
            "group": group,
            **_filter_params(
                q=q, ad_format=ad_format, advertiser_type=advertiser_type, creative_lang=creative_lang,
                channel_country=channel_country, channel_lang=channel_lang, category_ids=category_ids,
                channel=channel, button_text=button_text, color_id=color_id, from_date=from_date,
                to_date=to_date, date_field=date_field,
            ),
        }
        return self._get("/public/v1/ads/timeline", params, model=AdsTimeline)

    def by_advertiser(
        self, domain: str, *, ad_format: AdFormat | None = None, advertiser_type: AdvertiserType | None = None,
        creative_lang: str | None = None, from_date: str | None = None, to_date: str | None = None,
        date_field: DateField = "last_seen", sort: AdSort = "last_seen", order: Order = "desc",
        limit: int = 20, cursor: str | None = None,
    ) -> SyncCursorPage[AdSummary]:
        """All ads pointing at a given advertiser ``domain`` (auto-paginating)."""
        params = {
            "ad_format": ad_format, "advertiser_type": advertiser_type, "creative_lang": creative_lang,
            "from_date": from_date, "to_date": to_date, "date_field": date_field,
            "sort": sort, "order": order, "limit": limit, "cursor": cursor,
        }
        return self._page(f"/public/v1/advertisers/{quote_path(domain)}/ads", params, item_key="ads", model=AdSummary, page_cls=SyncCursorPage)


class AsyncAdsResource(AsyncResource):
    def search(
        self, q: str | None = None, *, ad_format: AdFormat | None = None,
        advertiser_type: AdvertiserType | None = None, creative_lang: str | None = None,
        channel_country: str | None = None, channel_lang: str | None = None,
        category_ids: Iterable[int] | str | None = None, channel: str | None = None,
        button_text: str | None = None, color_id: int | None = None, from_date: str | None = None,
        to_date: str | None = None, date_field: DateField = "last_seen", sort: AdSort = "last_seen",
        order: Order = "desc", limit: int = 20, cursor: str | None = None,
    ) -> AsyncPaginator[AdSummary]:
        """Search the Telegram Ads creatives index (auto-paginating)."""
        params = {
            **_filter_params(
                q=q, ad_format=ad_format, advertiser_type=advertiser_type, creative_lang=creative_lang,
                channel_country=channel_country, channel_lang=channel_lang, category_ids=category_ids,
                channel=channel, button_text=button_text, color_id=color_id, from_date=from_date,
                to_date=to_date, date_field=date_field,
            ),
            "sort": sort, "order": order, "limit": limit, "cursor": cursor,
        }
        return self._page("/public/v1/ads/search", params, item_key="ads", model=AdSummary, page_cls=AsyncCursorPage)

    async def get(self, creative_hash: str) -> AdCreative:
        """The full creative card for one ad."""
        return await self._get(f"/public/v1/ads/{quote_path(creative_hash)}", None, model=AdCreative)

    async def facets(
        self, q: str | None = None, *, ad_format: AdFormat | None = None,
        advertiser_type: AdvertiserType | None = None, creative_lang: str | None = None,
        channel_country: str | None = None, channel_lang: str | None = None,
        category_ids: Iterable[int] | str | None = None, channel: str | None = None,
        button_text: str | None = None, color_id: int | None = None,
        from_date: str | None = None, to_date: str | None = None, date_field: DateField = "last_seen",
    ) -> AdFacets:
        """Available filter values (facets) for the current ad query."""
        params = _filter_params(
            q=q, ad_format=ad_format, advertiser_type=advertiser_type, creative_lang=creative_lang,
            channel_country=channel_country, channel_lang=channel_lang, category_ids=category_ids,
            channel=channel, button_text=button_text, color_id=color_id, from_date=from_date,
            to_date=to_date, date_field=date_field,
        )
        return await self._get("/public/v1/ads/facets", params, model=AdFacets)

    async def timeline(
        self, q: str | None = None, *, group: Group = "month", ad_format: AdFormat | None = None,
        advertiser_type: AdvertiserType | None = None, creative_lang: str | None = None,
        channel_country: str | None = None, channel_lang: str | None = None,
        category_ids: Iterable[int] | str | None = None, channel: str | None = None,
        button_text: str | None = None, color_id: int | None = None,
        from_date: str | None = None, to_date: str | None = None, date_field: DateField = "last_seen",
    ) -> AdsTimeline:
        """Ad-volume time series for the current query."""
        params = {
            "group": group,
            **_filter_params(
                q=q, ad_format=ad_format, advertiser_type=advertiser_type, creative_lang=creative_lang,
                channel_country=channel_country, channel_lang=channel_lang, category_ids=category_ids,
                channel=channel, button_text=button_text, color_id=color_id, from_date=from_date,
                to_date=to_date, date_field=date_field,
            ),
        }
        return await self._get("/public/v1/ads/timeline", params, model=AdsTimeline)

    def by_advertiser(
        self, domain: str, *, ad_format: AdFormat | None = None, advertiser_type: AdvertiserType | None = None,
        creative_lang: str | None = None, from_date: str | None = None, to_date: str | None = None,
        date_field: DateField = "last_seen", sort: AdSort = "last_seen", order: Order = "desc",
        limit: int = 20, cursor: str | None = None,
    ) -> AsyncPaginator[AdSummary]:
        """All ads pointing at a given advertiser ``domain`` (auto-paginating)."""
        params = {
            "ad_format": ad_format, "advertiser_type": advertiser_type, "creative_lang": creative_lang,
            "from_date": from_date, "to_date": to_date, "date_field": date_field,
            "sort": sort, "order": order, "limit": limit, "cursor": cursor,
        }
        return self._page(f"/public/v1/advertisers/{quote_path(domain)}/ads", params, item_key="ads", model=AdSummary, page_cls=AsyncCursorPage)
