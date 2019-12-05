from typing import Tuple, Union

from eth_typing import Hash32

from ssz.exceptions import DeserializationError, SerializationError
from ssz.sedes.byte import byte
from ssz.sedes.vector import Vector
from ssz.typing import CacheObj
from ssz.utils import merkleize, merkleize_with_cache, pack_bytes

BytesOrByteArray = Union[bytes, bytearray]


class ByteVector(Vector[BytesOrByteArray, bytes]):
    """Equivalent to `Vector(byte, size)` but more efficient."""

    def __init__(self, size: int) -> None:
        super().__init__(element_sedes=byte, length=size)

    def serialize(self, value: BytesOrByteArray) -> bytes:
        if len(value) != self.length:
            raise SerializationError(
                f"Cannot serialize length {len(value)} byte-string as bytes{self.length}"
            )

        return value

    def serialize_element_for_tree(self, index: int, byte_value: int) -> bytes:
        if not 0 <= byte_value < 256:
            raise SerializationError(
                f"Cannot serialize byte as its value {byte_value} is invalid"
            )

        return bytes((byte_value,))

    def deserialize(self, data: bytes) -> bytes:
        if len(data) != self.length:
            raise DeserializationError(
                f"Cannot deserialize length {len(data)} data as bytes{self.length}"
            )
        return data

    def get_hash_tree_root(self, value: bytes) -> bytes:
        serialized_value = self.serialize(value)
        return merkleize(pack_bytes(serialized_value))

    def get_hash_tree_root_and_leaves(
        self, value: bytes, cache: CacheObj
    ) -> Tuple[Hash32, CacheObj]:
        serialized_value = self.serialize(value)
        return merkleize_with_cache(pack_bytes(serialized_value), cache=cache)

    def get_sedes_id(self) -> str:
        return f"{self.__class__.__name__}{self.length}"


bytes1 = ByteVector(1)
bytes4 = ByteVector(4)
bytes8 = ByteVector(8)
bytes32 = ByteVector(32)
bytes48 = ByteVector(48)
bytes96 = ByteVector(96)
