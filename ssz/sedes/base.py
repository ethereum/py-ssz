from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Generic,
    Tuple,
    TypeVar,
)

from ssz.exceptions import (
    DeserializationError,
    SerializationError,
)


T = TypeVar("T")
S = TypeVar("S")


class BaseSedes(ABC, Generic[T, S]):

    @abstractmethod
    def serialize(self, value: T) -> bytes:
        pass

    @abstractmethod
    def deserialize_segment(self, data: bytes, start_index: int) -> Tuple[S, int]:
        pass

    def deserialize(self, data: bytes) -> S:
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
                f"Tried to read {num_bytes} bytes from {start_index} but the string is only "
                f"{len(data)} bytes long"
            )
        else:
            continuation_index = start_index + num_bytes
            return data[start_index:start_index + num_bytes], continuation_index


class FixedSizedSedes(BaseSedes[T, S]):

    def __init__(self, length: int):
        if length <= 0:
            raise ValueError("Length must be greater than 0")

        self.length = length

    #
    # Serialization
    #
    def serialize(self, value: T) -> bytes:
        return self.serialize_content(value)

    @abstractmethod
    def serialize_content(self, value: T) -> bytes:
        pass

    #
    # Deserialization
    #
    def deserialize_segment(self, data: bytes, start_index: int) -> Tuple[S, int]:
        content, continuation_index = self.consume_bytes(data, start_index, self.length)
        return self.deserialize_content(content), continuation_index

    @abstractmethod
    def deserialize_content(self, content: bytes) -> S:
        pass


class LengthPrefixedSedes(BaseSedes[T, S]):

    #
    # Prefix helpers
    #
    @property
    @abstractmethod
    def length_bytes(self) -> int:
        pass

    @property
    def max_content_length(self) -> int:
        return 2 ** (self.length_bytes * 8) - 1

    def get_length_prefix(self, content: bytes) -> bytes:
        return len(content).to_bytes(self.length_bytes, "big")

    def validate_content_length(self, content: bytes) -> None:
        if len(content) >= self.max_content_length:
            raise SerializationError(
                f"Content is too big to be encoded in prefix of {self.length_bytes} bytes",
            )

    #
    # Serialization
    #
    def serialize(self, value: T) -> bytes:
        content = self.serialize_content(value)
        self.validate_content_length(content)
        return self.get_length_prefix(content) + content

    @abstractmethod
    def serialize_content(self, value: T) -> bytes:
        pass

    #
    # Deserialization
    #
    def deserialize_segment(self, data: bytes, start_index: int) -> Tuple[S, int]:
        prefix, content_start_index = self.consume_bytes(data, start_index, self.length_bytes)
        length = int.from_bytes(prefix, "big")
        content, continuation_index = self.consume_bytes(data, content_start_index, length)
        return self.deserialize_content(content), continuation_index

    @abstractmethod
    def deserialize_content(self, content: bytes) -> S:
        pass
