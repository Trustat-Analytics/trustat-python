"""Trustat — the Python SDK for the Trustat API.

Quickstart::

    from trustat import Trustat

    with Trustat(api_key="tk_...") as client:
        channel = client.channels.get("durov")
        print(channel.title, channel.participants)

        for post in client.posts.search(q="bitcoin", limit=50):
            print(post.message_id, post.views)

Async::

    from trustat import AsyncTrustat

    async with AsyncTrustat(api_key="tk_...") as client:
        async for ch in client.channels.search(q="news"):
            print(ch.title)
"""

from __future__ import annotations

from . import errors, types
from ._client import AsyncTrustat, Trustat
from ._rate_limit import Quota, RateLimit
from ._version import __version__
from .errors import *  # noqa: F401,F403
from .errors import __all__ as _errors_all
from .pagination import (
    AsyncCursorPage,
    AsyncOffsetPage,
    SyncCursorPage,
    SyncOffsetPage,
)
from .types import *  # noqa: F401,F403
from .types import __all__ as _types_all

__all__ = [
    "Trustat",
    "AsyncTrustat",
    "__version__",
    "RateLimit",
    "Quota",
    "SyncCursorPage",
    "AsyncCursorPage",
    "SyncOffsetPage",
    "AsyncOffsetPage",
    "errors",
    "types",
    *_errors_all,
    *_types_all,
]
