"""Public type surface: Literal aliases for closed parameter sets + the response
models (re-exported from the generated layer).

Import models from here or from the package root: ``from trustat import ChannelInfo``.
"""

from __future__ import annotations

from typing import Literal

from ._models.models import (
    AdCreative,
    AdFacets,
    AdsTimeline,
    AdSummary,
    AdvertiserAdsList,
    CategoryDict,
    ChannelInfo,
    ChannelStat,
    CountryDict,
    FacetBucket,
    Forward,
    HealthStatus,
    LanguageDict,
    LookupResponse,
    LookupResult,
    Mention,
    Post,
    PostHistory,
    PostStat,
    PostSummary,
    PostVersion,
    SubscribersPoint,
    SubscribersSeries,
    TimelinePoint,
    UsageInfo,
    VersionInfo,
    ViewsPoint,
    ViewsSeries,
)

# --- Literal aliases for closed parameter sets (autocomplete + type-checking) ---
Source = Literal["telegram", "max"]
LookupSource = Literal["telegram", "max", "all"]
Order = Literal["asc", "desc"]
Group = Literal["day", "week", "month"]
PeerType = Literal["channel", "chat", "all"]
ChannelSort = Literal["subscribers", "views", "growth_day", "growth_week"]
PostSort = Literal["date", "views"]
AdSort = Literal["last_seen", "first_seen"]
AdFormat = Literal["image", "premium_emoji", "text", "video"]
AdvertiserType = Literal["website", "channel", "bot"]
DateField = Literal["first_seen", "last_seen"]

__all__ = [
    "Source",
    "LookupSource",
    "Order",
    "Group",
    "PeerType",
    "ChannelSort",
    "PostSort",
    "AdSort",
    "AdFormat",
    "AdvertiserType",
    "DateField",
    "AdCreative",
    "AdFacets",
    "AdsTimeline",
    "AdSummary",
    "AdvertiserAdsList",
    "CategoryDict",
    "ChannelInfo",
    "ChannelStat",
    "CountryDict",
    "FacetBucket",
    "Forward",
    "HealthStatus",
    "LanguageDict",
    "LookupResponse",
    "LookupResult",
    "Mention",
    "Post",
    "PostHistory",
    "PostStat",
    "PostSummary",
    "PostVersion",
    "SubscribersPoint",
    "SubscribersSeries",
    "TimelinePoint",
    "UsageInfo",
    "VersionInfo",
    "ViewsPoint",
    "ViewsSeries",
]
