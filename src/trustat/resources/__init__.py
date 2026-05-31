"""Resource namespaces exposed on the client (``client.channels``, etc.)."""

from __future__ import annotations

from .ads import AdsResource, AsyncAdsResource
from .channels import AsyncChannelsResource, ChannelsResource
from .dictionaries import AsyncDictionariesResource, DictionariesResource
from .lookup import AsyncLookupResource, LookupResource
from .posts import AsyncPostsResource, PostsResource
from .system import AsyncSystemResource, SystemResource
from .usage import AsyncUsageResource, UsageResource

__all__ = [
    "ChannelsResource",
    "AsyncChannelsResource",
    "PostsResource",
    "AsyncPostsResource",
    "AdsResource",
    "AsyncAdsResource",
    "LookupResource",
    "AsyncLookupResource",
    "DictionariesResource",
    "AsyncDictionariesResource",
    "UsageResource",
    "AsyncUsageResource",
    "SystemResource",
    "AsyncSystemResource",
]
