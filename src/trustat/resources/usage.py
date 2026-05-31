"""The ``usage`` namespace: current quota consumption for your key."""

from __future__ import annotations

from .._models.models import UsageInfo
from ._base import AsyncResource, SyncResource


class UsageResource(SyncResource):
    def info(self) -> UsageInfo:
        """Current monthly quota consumption (requests / unique channels / listing)."""
        return self._get("/public/v1/usage/info", None, model=UsageInfo)


class AsyncUsageResource(AsyncResource):
    async def info(self) -> UsageInfo:
        """Current monthly quota consumption (requests / unique channels / listing)."""
        return await self._get("/public/v1/usage/info", None, model=UsageInfo)
