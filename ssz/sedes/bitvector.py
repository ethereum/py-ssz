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
    get_serialized_bytearray,
    merkleize,
    pack_bits,
)

BytesOrByteArray = Union[bytes, bytearray]


class Bitvector(BaseCompositeSedes[BytesOrByteArray, bytes]):
    def __init__(self, bit_count: int) -> None:
        if bit_count < 0:
            raise TypeError("Bit count cannot be negative")
        self.bit_count = bit_count

    #
    # Size
    #
    is_fixed_sized = True

    def get_fixed_size(self):
        return (self.bit_count + 7) // 8

    #
    # Serialization
    #
    def serialize(self, value: Sequence[bool]) -> bytes:
        if len(value) != self.bit_count:
            raise SerializationError(
                f"Cannot serialize length {len(value)} bit array as Bitvector[{self.bit_count}]"
            )
        return bytes(get_serialized_bytearray(value, self.bit_count))

    def _get_empty_bytearray(self) -> bytearray:
        return bytearray((self.bit_count + 7) // 8)

    #
    # Deserialization
    #
    def deserialize(self, data: bytes) -> bytes:
        if len(data) * 8 > self.bit_count:
            raise DeserializationError(
                f"Cannot deserialize length {len(data)} bytes data as Bitvector[{self.bit_count}]"
            )

        return tuple(
            bool((data[index // 8] >> index % 8) % 2)
            for index in range(self.bit_count)
        )

    #
    # Tree hashing
    #
    def hash_tree_root(self, value: Sequence[bool]) -> bytes:
        return merkleize(pack_bits(value))
