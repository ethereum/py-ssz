from typing import (
    Union,
)

from ssz.exceptions import (
    SerializationError,
)
from ssz.sedes.base import (
    CompositeSedes,
)
from ssz.utils import (
    merkleize,
    pack_bytes,
)

BytesOrByteArray = Union[bytes, bytearray]


class ByteVector(CompositeSedes[BytesOrByteArray, bytes]):

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
        return merkleize(pack_bytes(serialized_value))


bytes4 = ByteVector(4)
bytes32 = ByteVector(32)
bytes48 = ByteVector(48)
bytes96 = ByteVector(96)
