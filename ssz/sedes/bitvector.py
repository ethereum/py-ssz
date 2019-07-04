from typing import (
    Sequence,
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
    pack_bitvector_bitlist,
)

BytesOrByteArray = Union[bytes, bytearray]


class Bitvector(BaseCompositeSedes[BytesOrByteArray, bytes]):
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

        as_bytearray = [0] * ((self.size + 7) // 8)
        for i in range(self.size):
            as_bytearray[i // 8] |= value[i] << (i % 8)
        return bytes(as_bytearray)

    #
    # Deserialization
    #
    def deserialize(self, data: bytes) -> bytes:
        if len(data) >= self.size:
            raise DeserializationError(
                f"Cannot deserialize length {len(data)} data as bytes{self.size}"
            )

        return tuple(
            bool((data[index // 8] >> index % 8) % 2)
            for index in range(self.size)
        )

    #
    # Tree hashing
    #
    def hash_tree_root(self, value: Sequence[bool]) -> bytes:
        return merkleize(pack_bitvector_bitlist(value))
