"""The ``system`` namespace: service health and version (root, unauthenticated)."""

from __future__ import annotations

from .._models.models import HealthStatus, VersionInfo
from ._base import AsyncResource, SyncResource


class SystemResource(SyncResource):
    def health(self) -> HealthStatus:
        """Liveness probe."""
        return self._get("/health", None, model=HealthStatus)

    def version(self) -> VersionInfo:
        """Service version."""
        return self._get("/version", None, model=VersionInfo)


class AsyncSystemResource(AsyncResource):
    async def health(self) -> HealthStatus:
        """Liveness probe."""
        return await self._get("/health", None, model=HealthStatus)

    async def version(self) -> VersionInfo:
        """Service version."""
        return await self._get("/version", None, model=VersionInfo)
