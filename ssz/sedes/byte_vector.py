from typing import Tuple, Union

from eth_typing import Hash32

from ssz.exceptions import DeserializationError, SerializationError
from ssz.sedes.base import BaseSedes
from ssz.sedes.basic import BasicBytesSedes
from ssz.typing import CacheObj
from ssz.utils import merkleize, merkleize_with_cache, pack_bytes

BytesOrByteArray = Union[bytes, bytearray]


class ByteVector(BasicBytesSedes[BytesOrByteArray, bytes]):
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
    def get_element_sedes(self, index: int) -> BaseSedes:
        raise NotImplementedError()

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

    def get_hash_tree_root_and_leaves(
        self, value: bytes, cache: CacheObj
    ) -> Tuple[Hash32, CacheObj]:
        serialized_value = self.serialize(value)
        return merkleize_with_cache(pack_bytes(serialized_value), cache=cache)

    def chunk_count(self) -> int:
        return self.length * self.size

    def get_sedes_id(self) -> str:
        return f"{self.__class__.__name__}{self.size}"


bytes1 = ByteVector(1)
bytes4 = ByteVector(4)
bytes8 = ByteVector(8)
bytes32 = ByteVector(32)
bytes48 = ByteVector(48)
bytes96 = ByteVector(96)
