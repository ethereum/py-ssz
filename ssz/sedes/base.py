from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Generic,
    Tuple,
    TypeVar,
)

from ssz.constants import (
    EMPTY_CHUNK,
)
from ssz.exceptions import (
    DeserializationError,
    SerializationError,
)

TSerializable = TypeVar("TSerializable")
TDeserialized = TypeVar("TDeserialized")


class BaseSedes(ABC, Generic[TSerializable, TDeserialized]):

    #
    # Size
    #
    @property
    @abstractmethod
    def is_static_sized(self) -> bool:
        pass

    @abstractmethod
    def get_static_size(self) -> int:
        pass

    #
    # Serialization
    #
    @abstractmethod
    def serialize(self, value: TSerializable) -> bytes:
        pass

    #
    # Deserialization
    #
    @abstractmethod
    def deserialize_segment(self, data: bytes, start_index: int) -> Tuple[TDeserialized, int]:
        pass

    def deserialize(self, data: bytes) -> TDeserialized:
        value, end_index = self.deserialize_segment(data, 0)

        num_leftover_bytes = len(data) - end_index
        if num_leftover_bytes > 0:
            raise DeserializationError(
                f"The given string ends with {num_leftover_bytes} superfluous bytes",
                data,
            )
        elif num_leftover_bytes < 0:
            raise Exception(
                "Invariant: End index cannot exceed size of data"
            )

        return value

    @staticmethod
    def consume_bytes(data: bytes, start_index: int, num_bytes: int) -> Tuple[bytes, int]:
        if start_index < 0:
            raise ValueError("Start index must not be negative")
        elif num_bytes < 0:
            raise ValueError("Number of bytes to read must not be negative")
        elif start_index + num_bytes > len(data):
            raise DeserializationError(
                f"Tried to read {num_bytes} bytes starting at index {start_index} but the string "
                f"is only {len(data)} bytes long"
            )
        else:
            continuation_index = start_index + num_bytes
            return data[start_index:start_index + num_bytes], continuation_index

    #
    # Tree hashing
    #
    def hash_tree_root(self, value: TSerializable) -> bytes:
        return EMPTY_CHUNK


class BasicSedes(BaseSedes[TSerializable, TDeserialized]):

    def __init__(self, size: int):
        if size <= 0:
            raise ValueError("Length must be greater than 0")

        self.size = size

    #
    # Size
    #
    is_static_sized = True

    def get_static_size(self):
        return self.size

    #
    # Serialization
    #
    def serialize(self, value: TSerializable) -> bytes:
        serialized_content = self.serialize_content(value)
        if len(serialized_content) != self.size:
            raise SerializationError(f"Cannot serialize {value} in {self.size} bytes")
        return serialized_content

    @abstractmethod
    def serialize_content(self, value: TSerializable) -> bytes:
        pass

    #
    # Deserialization
    #
    def deserialize_segment(self, data: bytes, start_index: int) -> Tuple[TDeserialized, int]:
        content, continuation_index = self.consume_bytes(data, start_index, self.size)
        return self.deserialize_content(content), continuation_index

    @abstractmethod
    def deserialize_content(self, content: bytes) -> TDeserialized:
        pass


class LengthPrefixedSedes(Generic[TSerializable, TDeserialized]):
    pass


class FixedSizedSedes(Generic[TSerializable, TDeserialized]):

    def __init__(self, size):
        pass
