from typing import (
    Union,
)

from ssz.exceptions import (
    DeserializationError,
    SerializationError,
)
from ssz.sedes.base import (
    BaseCompositeSedes,
)
from ssz.utils import (
    merkleize,
    pack_bytes,
)

BytesOrByteArray = Union[bytes, bytearray]


class ByteVector(BaseCompositeSedes[BytesOrByteArray, bytes]):
    def __init__(self, size: int) -> None:
        if size < 0:
            raise TypeError("Size cannot be negative")
        self.size = size

    #
    # Size
    #
    is_fixed_sized = True

    def get_fixed_size(self):
        return self.size

    #
    # Serialization
    #
    def serialize(self, value: BytesOrByteArray) -> bytes:
        if len(value) != self.size:
            raise SerializationError(
                f"Cannot serialize length {len(value)} byte-string as bytes{self.size}"
            )

        return value

    #
    # Deserialization
    #
    def deserialize(self, data: bytes) -> bytes:
        if len(data) != self.size:
            raise DeserializationError(
                f"Cannot deserialize length {len(data)} data as bytes{self.size}"
            )
        return data

    #
    # Tree hashing
    #
    def get_hash_tree_root(self, value: bytes) -> bytes:
        serialized_value = self.serialize(value)
        return merkleize(pack_bytes(serialized_value))

    def get_hash_tree_root_and_leaves(self, value: bytes, db) -> bytes:
        serialized_value = self.serialize(value)
        root, db = merkleize(
            pack_bytes(serialized_value),
            db=db,
        )
        return root, db

    def chunk_count(self) -> int:
        return self.length * self.size


bytes1 = ByteVector(1)
bytes4 = ByteVector(4)
bytes8 = ByteVector(8)
bytes32 = ByteVector(32)
bytes48 = ByteVector(48)
bytes96 = ByteVector(96)
