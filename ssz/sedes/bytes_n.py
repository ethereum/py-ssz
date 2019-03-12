from typing import (
    Union,
)

from ssz.exceptions import (
    SerializationError,
)
from ssz.utils import (
    merkleize,
    pack,
)
from ssz.sedes.tuple import (
    CompositeSedes,
)

BytesOrByteArray = Union[bytes, bytearray]


class ByteTuple(CompositeSedes[BytesOrByteArray, bytes]):

    def __init__(self, length: int) -> None:
        self.length = length

    #
    # Size
    #
    is_variable_length = False

    def get_fixed_length(self):
        return self.length

    #
    # Serialization
    #
    def serialize_content(self, value: BytesOrByteArray) -> bytes:
        if len(value) != self.length:
            raise SerializationError(
                f"Cannot serialize {len(value)} elements as bytes{self.length}"
            )

        return value

    #
    # Deserialization
    #
    def deserialize_content(self, content: bytes) -> bytes:
        return content

    #
    # Tree hashing
    #
    def hash_tree_root(self, value: bytes) -> bytes:
        serialized_value = self.serialize(value)
        return merkleize(pack(serialized_value))


bytes32 = ByteTuple(32)
bytes48 = ByteTuple(48)
bytes96 = ByteTuple(96)
