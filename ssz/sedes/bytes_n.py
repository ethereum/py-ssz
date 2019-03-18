from typing import (
    Union,
)

from ssz.exceptions import (
    SerializationError,
)
from ssz.sedes.tuple import (
    CompositeSedes,
)
from ssz.utils import (
    merkleize,
    pack,
)

BytesOrByteArray = Union[bytes, bytearray]


class ByteTuple(CompositeSedes[BytesOrByteArray, bytes]):

    def __init__(self, size: int) -> None:
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
    def serialize_content(self, value: BytesOrByteArray) -> bytes:
        if len(value) != self.size:
            raise SerializationError(
                f"Cannot serialize {len(value)} bytes as bytes{self.size}"
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
