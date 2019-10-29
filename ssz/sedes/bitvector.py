from typing import Sequence, Tuple, Union

from eth_typing import Hash32
from eth_utils import to_tuple

from ssz.exceptions import DeserializationError, SerializationError
from ssz.sedes.base import BaseSedes
from ssz.sedes.basic import BasicBytesSedes
from ssz.typing import CacheObj
from ssz.utils import (
    get_serialized_bytearray,
    merkleize,
    merkleize_with_cache,
    pack_bits,
)

BytesOrByteArray = Union[bytes, bytearray]


class Bitvector(BasicBytesSedes[BytesOrByteArray, bytes]):
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
    def get_element_sedes(self, index: int) -> BaseSedes:
        # TODO: find better place to define abstractmethod to avoid having to implement it here
        raise NotImplementedError()

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

    def get_hash_tree_root_and_leaves(
        self, value: Sequence[bool], cache: CacheObj
    ) -> Tuple[Hash32, CacheObj]:
        chunk_count = (self.bit_count + 255) // 256
        return merkleize_with_cache(pack_bits(value), cache=cache, limit=chunk_count)

    def chunk_count(self) -> int:
        return (self.bit_count + 255) // 256

    def get_sedes_id(self) -> str:
        return f"{self.__class__.__name__}{self.bit_count}"
