#
# Copied from PyEVM codebase
#
from lru import LRU

from abc import (
    ABC,
    abstractmethod
)
from collections.abc import (
    MutableMapping,
)

from typing import (
    Any,
    Dict,
    Iterator,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    MM = MutableMapping[bytes, bytes]
else:
    MM = MutableMapping


class BaseDB(MM, ABC):
    """
    This is an abstract key/value lookup with all :class:`bytes` values,
    with some convenience methods for databases. As much as possible,
    you can use a DB as if it were a :class:`dict`.

    Notable exceptions are that you cannot iterate through all values or get the length.
    (Unless a subclass explicitly enables it).

    All subclasses must implement these methods:
    __init__, __getitem__, __setitem__, __delitem__

    Subclasses may optionally implement an _exists method
    that is type-checked for key and value.
    """

    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError(
            "The `init` method must be implemented by subclasses of BaseDB"
        )

    def set(self, key: bytes, value: bytes) -> None:
        self[key] = value

    def exists(self, key: bytes) -> bool:
        return self.__contains__(key)

    def __contains__(self, key: bytes) -> bool:     # type: ignore # Breaks LSP
        if hasattr(self, '_exists'):
            # Classes which inherit this class would have `_exists` attr
            return self._exists(key)    # type: ignore
        else:
            return super().__contains__(key)

    def delete(self, key: bytes) -> None:
        try:
            del self[key]
        except KeyError:
            return None

    def __iter__(self) -> Iterator[bytes]:
        raise NotImplementedError("By default, DB classes cannot be iterated.")

    def __len__(self) -> int:
        raise NotImplementedError("By default, DB classes cannot return the total number of keys.")


class BaseAtomicDB(BaseDB):
    """
    This is an abstract key/value lookup that permits batching of updates, such that the batch of
    changes are atomically saved. They are either all saved, or none are.

    Writes to the database are immediately saved, unless they are explicitly batched
    in a context, like this:

    ::

        atomic_db = AtomicDB()
        with atomic_db.atomic_batch() as db:
            # changes are not immediately saved to the db, inside this context
            db[key] = val

            # changes are still locally visible even though they are not yet committed to the db
            assert db[key] == val

            if some_bad_condition:
                raise Exception("something went wrong, erase all the pending changes")

            db[key2] = val2
            # when exiting the context, the values are saved either key and key2 will both be saved,
            # or neither will
    """
    @abstractmethod
    def atomic_batch(self) -> Any:
        raise NotImplementedError


class MemoryDB(BaseDB):
    kv_store = None  # type: Dict[bytes, bytes]

    def __init__(self, kv_store: Dict[bytes, bytes] = None) -> None:
        if kv_store is None:
            self.kv_store = {}
        else:
            self.kv_store = kv_store

    def __getitem__(self, key: bytes) -> bytes:
        return self.kv_store[key]

    def __setitem__(self, key: bytes, value: bytes) -> None:
        self.kv_store[key] = value

    def _exists(self, key: bytes) -> bool:
        return key in self.kv_store

    def __delitem__(self, key: bytes) -> None:
        del self.kv_store[key]

    def __iter__(self) -> Iterator[bytes]:
        return iter(self.kv_store)

    def __len__(self) -> int:
        return len(self.kv_store)

    def __repr__(self) -> str:
        return "MemoryDB(%r)" % self.kv_store


class CacheDB(BaseDB):
    """
    Set and get decoded RLP objects, where the underlying db stores
    encoded objects.
    """
    def __init__(self, db: BaseDB, cache_size: int=2048) -> None:
        self._db = db
        self._cache_size = cache_size
        self.reset_cache()

    def reset_cache(self) -> None:
        self._cached_values = LRU(self._cache_size)

    def __getitem__(self, key: bytes) -> bytes:
        if key not in self._cached_values:
            self._cached_values[key] = self._db[key]
        return self._cached_values[key]

    def __setitem__(self, key: bytes, value: bytes) -> None:
        self._cached_values[key] = value
        self._db[key] = value

    def __delitem__(self, key: bytes) -> None:
        if key in self._cached_values:
            del self._cached_values[key]
        del self._db[key]
