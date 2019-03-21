from typing import (
    Generator,
    Sequence,
    Tuple,
    TypeVar,
)

from eth_utils import (
    to_tuple,
)

from ssz.exceptions import (
    DeserializationError,
    SerializationError,
)
from ssz.sedes.base import (
    BaseSedes,
    BasicSedes,
    CompositeSedes,
)
from ssz.utils import (
    merkleize,
    pack,
)

TSerializableElement = TypeVar("TSerializable")
TDeserializedElement = TypeVar("TDeserialized")


class Vector(CompositeSedes[Sequence[TSerializableElement], Tuple[TDeserializedElement, ...]]):

    def __init__(self,
                 element_sedes: BaseSedes[TSerializableElement, TDeserializedElement],
                 length: int) -> None:

        self.length = length
        self.element_sedes = element_sedes

    #
    # Size
    #
    @property
    def is_static_sized(self) -> bool:
        return self.element_sedes.is_static_sized or self.length == 0

    def get_static_size(self) -> int:
        if not self.is_static_sized:
            raise ValueError("Tuple does not have a fixed length")

        if self.length == 0:
            return 0
        else:
            return self.length * self.element_sedes.get_static_size()

    #
    # Serialization
    #
    def serialize_content(self, value: Sequence[TSerializableElement]) -> bytes:
        if isinstance(value, (bytes, bytearray, str)):
            raise SerializationError("Can not serialize strings as tuples")

        if len(value) != self.length:
            raise SerializationError(
                f"Cannot serialize {len(value)} elements as {self.length}-tuple"
            )

        return b"".join(
            self.element_sedes.serialize(element) for element in value
        )

    #
    # Deserialization
    #
    @to_tuple
    def deserialize_content(self, content: bytes) -> Generator[TDeserializedElement, None, None]:
        element_start_index = 0
        for element_index in range(self.length):
            element, next_element_start_index = self.element_sedes.deserialize_segment(
                content,
                element_start_index,
            )

            if next_element_start_index <= element_start_index:
                raise Exception("Invariant: must always make progress")
            element_start_index = next_element_start_index

            yield element

        if element_start_index > len(content):
            raise Exception("Invariant: must not consume more data than available")
        if element_start_index < len(content):
            raise DeserializationError(
                f"Serialized tuple ends with {len(content) - element_start_index} extra bytes"
            )

    #
    # Tree hashing
    #
    def hash_tree_root(self, value: Sequence[TSerializableElement]) -> bytes:
        if isinstance(self.element_sedes, BasicSedes):
            serialized_elements = tuple(
                self.element_sedes.serialize(element)
                for element in value
            )
            return merkleize(pack(serialized_elements))
        else:
            element_tree_hashes = tuple(
                self.element_sedes.hash_tree_root(element)
                for element in value
            )
            return merkleize(element_tree_hashes)
