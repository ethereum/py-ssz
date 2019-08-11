from typing import (
    Sequence,
    Union,
)

from eth_utils import (
    to_tuple,
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
        return bytes(get_serialized_bytearray(value, self.bit_count, extra_byte=False))

    #
    # Deserialization
    #
    @to_tuple
    def deserialize(self, data: bytes) -> bytes:
        if len(data) > (self.bit_count + 7) // 8:
            raise DeserializationError(
                f"Cannot deserialize length {len(data)} bytes data as Bitvector[{self.bit_count}]"
            )

        for bit_index in range(self.bit_count):
            yield bool((data[bit_index // 8] >> bit_index % 8) % 2)

    #
    # Tree hashing
    #
    def get_hash_tree_root(self, value: Sequence[bool]) -> bytes:
        chunk_count = (self.bit_count + 255) // 256
        return merkleize(pack_bits(value), limit=chunk_count)

    def get_hash_tree_root_and_leaves(self, value: Sequence[bool], merkle_leaves_dict) -> bytes:
        chunk_count = (self.bit_count + 255) // 256
        root, merkle_leaves_dict = merkleize(
            pack_bits(value),
            limit=chunk_count,
            merkle_leaves_dict=merkle_leaves_dict,
        )
        return root, merkle_leaves_dict

    def chunk_count(self) -> int:
        return (self.bit_count + 255) // 256
