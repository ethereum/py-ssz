from typing import Any, Sequence, Tuple, Union

from eth_typing import Hash32
from eth_utils import to_tuple

from ssz.exceptions import DeserializationError, SerializationError
from ssz.sedes.basic import BitfieldCompositeSedes
from ssz.typing import CacheObj
from ssz.utils import (
    get_serialized_bytearray,
    merkleize,
    merkleize_with_cache,
    mix_in_length,
    pack_bits,
)

BytesOrByteArray = Union[bytes, bytearray]


class Bitlist(BitfieldCompositeSedes[BytesOrByteArray, bytes]):
    def __init__(self, max_bit_count: int) -> None:
        if max_bit_count < 0:
            raise TypeError("Max bit count cannot be negative")
        self.max_bit_count = max_bit_count

    #
    # Size
    #
    is_fixed_sized = False

    def get_fixed_size(self):
        raise ValueError("byte list has no static size")

    #
    # Serialization
    #
    @property
    def chunk_count(self) -> int:
        return (self.max_bit_count + 255) // 256

    def serialize(self, value: Sequence[bool]) -> bytes:
        len_value = len(value)
        if len_value > self.max_bit_count:
            raise SerializationError(
                f"Cannot serialize length {len_value} bit array as Bitlist[{self.max_bit_count}]"
            )

        serialized_bytearray = get_serialized_bytearray(
            value, len_value, extra_byte=True
        )
        serialized_bytearray[len_value // 8] |= 1 << (len_value % 8)
        return bytes(serialized_bytearray)

    #
    # Deserialization
    #
    @to_tuple
    def deserialize(self, data: bytes) -> Tuple[bool, ...]:
        as_integer = int.from_bytes(data, "little")
        len_value = get_bitlist_len(as_integer)

        if len_value > self.max_bit_count:
            raise DeserializationError(
                f"Cannot deserialize length {len_value} bytes data as Bitlist[{self.max_bit_count}]"
            )

        for bit_index in range(len_value):
            yield bool((data[bit_index // 8] >> bit_index % 8) % 2)

    #
    # Tree hashing
    #
    def get_hash_tree_root(self, value: Sequence[bool]) -> bytes:
        return mix_in_length(
            merkleize(pack_bits(value), limit=self.chunk_count), len(value)
        )

    def get_hash_tree_root_and_leaves(
        self, value: Sequence[bool], cache: CacheObj
    ) -> Tuple[Hash32, CacheObj]:
        root, cache = merkleize_with_cache(
            pack_bits(value), cache=cache, limit=self.chunk_count
        )
        return mix_in_length(root, len(value)), cache

    def get_sedes_id(self) -> str:
        return f"{self.__class__.__name__}{self.max_bit_count}"

    #
    # Equality and hashing
    #
    def __hash__(self) -> int:
        return hash((hash(Bitlist), hash(self.max_bit_count)))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Bitlist) and other.max_bit_count == self.max_bit_count


def get_bitlist_len(x: int) -> int:
    return x.bit_length() - 1
