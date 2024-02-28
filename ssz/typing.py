from collections.abc import (
    MutableMapping,
)
from typing import (
    NewType,
    TypeVar,
    Union,
)

TSerializable = TypeVar("TSerializable")
TDeserialized = TypeVar("TDeserialized")

TSerializableElement = TypeVar("TSerializableElement")
TDeserializedElement = TypeVar("TDeserializedElement")

CacheObj = NewType("CacheObj", Union[MutableMapping, dict])
