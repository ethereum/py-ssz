from collections.abc import MutableMapping
from typing import TYPE_CHECKING, Iterator

from lru import LRU

if TYPE_CHECKING:
    MM = MutableMapping[bytes, bytes]
else:
    MM = MutableMapping

DEFAULT_CACHE_SIZE = 2 ** 10


class SSZCache(MM):
    def __init__(self, cache_size: int = DEFAULT_CACHE_SIZE) -> None:
        self._cache_size = cache_size
        self.clear()

    def clear(self) -> None:
        self._cached_values = LRU(self._cache_size)

    def _exists(self, key: bytes) -> bool:
        return key in self._cached_values

    def __contains__(self, key: bytes) -> bool:
        return self._exists(key)

    def __getitem__(self, key: bytes) -> bytes:
        return self._cached_values[key]

    def __setitem__(self, key: bytes, value: bytes) -> None:
        self._cached_values[key] = value

    def __delitem__(self, key: bytes) -> None:
        if key in self._cached_values:
            del self._cached_values[key]
        else:
            raise KeyError(f"key: {key} not found")

    def __iter__(self) -> Iterator[bytes]:
        raise NotImplementedError("By default, DB classes cannot be iterated.")

    def __len__(self) -> int:
        raise NotImplementedError(
            "By default, classes cannot return the total number of keys."
        )

    @property
    def cache_size(self) -> int:
        return self._cache_size
