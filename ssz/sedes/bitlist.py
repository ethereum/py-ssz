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
    mix_in_length,
    pack_bitvector_bitlist,
)

BytesOrByteArray = Union[bytes, bytearray]


class Bitlist(BaseCompositeSedes[BytesOrByteArray, bytes]):
    def __init__(self, bit_count: int) -> None:
        if bit_count < 0:
            raise TypeError("Max bit count cannot be negative")
        self.bit_count = bit_count

    #
    # Size
    #
    is_fixed_sized = False

    def get_fixed_size(self):
        raise ValueError("byte list has no static size")

    #
    # Serialization
    #
    def serialize(self, value: Sequence[bool]) -> bytes:
        len_value = len(value)
        if len_value > self.bit_count:
            raise SerializationError(
                f"Cannot serialize length {len_value} bit array as Bitlist[{self.bit_count}]"
            )

        if len_value == 0:
            return b'\x01'

        as_bytearray = [0] * (len_value // 8 + 1)
        for i in range(len_value):
            as_bytearray[i // 8] |= value[i] << (i % 8)
        as_bytearray[len_value // 8] |= 1 << (len_value % 8)
        return bytes(as_bytearray)

    #
    # Deserialization
    #
    def deserialize(self, data: bytes) -> Tuple[bool, ...]:
        as_integer = int.from_bytes(data, 'little')
        len_value = get_bitlist_len(as_integer)

        if len_value > self.bit_count:
            raise DeserializationError(
                f"Cannot deserialize length {len_value} bytes data as Bitlist[{self.bit_count}]"
            )

        return tuple(
            bool((data[index // 8] >> index % 8) % 2)
            for index in range(len_value)
        )

    #
    # Tree hashing
    #
    def hash_tree_root(self, value: Sequence[bool]) -> bytes:
        return mix_in_length(merkleize(pack_bitvector_bitlist(value)), len(value))


def get_bitlist_len(x: int) -> int:
    return x.bit_length() - 1
