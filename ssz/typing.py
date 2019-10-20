from collections.abc import MutableMapping
from typing import NewType, TypeVar, Union

TSerializable = TypeVar("TSerializable")
TDeserialized = TypeVar("TDeserialized")

TSerializableElement = TypeVar("TSerializable")
TDeserializedElement = TypeVar("TDeserialized")

CacheObj = NewType("CacheObj", Union[MutableMapping, dict])
