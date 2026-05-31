"""The ``dictionaries`` namespace: category / country / language reference lists."""

from __future__ import annotations

from .._models.models import CategoryDict, CountryDict, LanguageDict
from ._base import AsyncResource, SyncResource


class DictionariesResource(SyncResource):
    def categories(self) -> list[CategoryDict]:
        """All channel categories with channel counts."""
        return self._get_list("/public/v1/dictionaries/categories", None, item_key="categories", model=CategoryDict)

    def countries(self) -> list[CountryDict]:
        """All channel countries with channel counts."""
        return self._get_list("/public/v1/dictionaries/countries", None, item_key="countries", model=CountryDict)

    def languages(self) -> list[LanguageDict]:
        """All channel languages with channel counts."""
        return self._get_list("/public/v1/dictionaries/languages", None, item_key="languages", model=LanguageDict)


class AsyncDictionariesResource(AsyncResource):
    async def categories(self) -> list[CategoryDict]:
        """All channel categories with channel counts."""
        return await self._get_list(
            "/public/v1/dictionaries/categories", None, item_key="categories", model=CategoryDict
        )

    async def countries(self) -> list[CountryDict]:
        """All channel countries with channel counts."""
        return await self._get_list("/public/v1/dictionaries/countries", None, item_key="countries", model=CountryDict)

    async def languages(self) -> list[LanguageDict]:
        """All channel languages with channel counts."""
        return await self._get_list("/public/v1/dictionaries/languages", None, item_key="languages", model=LanguageDict)
