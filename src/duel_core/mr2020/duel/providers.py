from __future__ import annotations

from typing import TypeVar, cast

_T = TypeVar("_T")


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[type[object], object] = {}

    def provide(self, provider: _T) -> _T:
        self._providers[type(provider)] = provider
        return provider

    def inject(self, key: type[_T]) -> _T:
        provider = self._providers.get(key)
        if provider is None:
            raise LookupError(f"{key.__name__} not provided")
        return cast(_T, provider)
