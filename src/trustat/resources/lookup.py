"""The ``lookup`` namespace: resolve any identifier/link to canonical ids.

The resource is callable for ergonomics: ``client.lookup("durov")`` or, more
explicitly, ``client.lookup.resolve("durov")``.
"""

from __future__ import annotations

from .._models.models import LookupResponse
from ..types import LookupSource
from ._base import AsyncResource, SyncResource


class LookupResource(SyncResource):
    def resolve(self, ref: str, *, source: LookupSource | None = None) -> LookupResponse:
        """Resolve an id / ``username`` / ``@username`` / t.me or max.ru link /
        ``<channel_id>_<message_id>`` to a canonical ``(source, channel_id[, message_id])``."""
        return self._get("/public/v1/lookup", {"ref": ref, "source": source}, model=LookupResponse)

    def __call__(self, ref: str, *, source: LookupSource | None = None) -> LookupResponse:
        return self.resolve(ref, source=source)


class AsyncLookupResource(AsyncResource):
    async def resolve(self, ref: str, *, source: LookupSource | None = None) -> LookupResponse:
        """Resolve an id / ``username`` / ``@username`` / t.me or max.ru link /
        ``<channel_id>_<message_id>`` to a canonical ``(source, channel_id[, message_id])``."""
        return await self._get("/public/v1/lookup", {"ref": ref, "source": source}, model=LookupResponse)

    async def __call__(self, ref: str, *, source: LookupSource | None = None) -> LookupResponse:
        return await self.resolve(ref, source=source)
