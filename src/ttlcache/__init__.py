"""A small LRU cache whose entries expire after a time-to-live."""
from __future__ import annotations

import time
from collections import OrderedDict
from typing import Any, Callable, Generic, Hashable, Optional, Tuple, TypeVar

__all__ = ["TTLCache"]

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")
_MISSING = object()


class TTLCache(Generic[K, V]):
    def __init__(self, maxsize: int, ttl: float, clock: Callable[[], float] = time.monotonic):
        if maxsize <= 0 or ttl <= 0:
            raise ValueError("maxsize and ttl must be positive")
        self.maxsize = maxsize
        self.ttl = ttl
        self._clock = clock
        self._data: "OrderedDict[K, Tuple[float, V]]" = OrderedDict()

    def set(self, key: K, value: V, ttl: Optional[float] = None) -> None:
        expires = self._clock() + (self.ttl if ttl is None else ttl)
        self._data[key] = (expires, value)
        self._data.move_to_end(key)
        self._purge()
        while len(self._data) > self.maxsize:
            self._data.popitem(last=False)

    def get(self, key: K, default: Any = None) -> Any:
        item = self._data.get(key, _MISSING)
        if item is _MISSING:
            return default
        expires, value = item  # type: ignore[misc]
        if expires <= self._clock():
            del self._data[key]
            return default
        self._data.move_to_end(key)
        return value

    def delete(self, key: K) -> bool:
        return self._data.pop(key, None) is not None

    def _purge(self) -> None:
        now = self._clock()
        for key in [k for k, (exp, _) in self._data.items() if exp <= now]:
            del self._data[key]

    def __len__(self) -> int:
        self._purge()
        return len(self._data)

    def __contains__(self, key: object) -> bool:
        return self.get(key, _MISSING) is not _MISSING  # type: ignore[arg-type]
