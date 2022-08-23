from typing import Union

from ssz.exceptions import DeserializationError, SerializationError
from ssz.sedes.byte import byte
from ssz.sedes.list import List
from ssz.utils import merkleize, mix_in_length, pack_bytes

BytesOrByteArray = Union[bytes, bytearray]


class ByteList(List[BytesOrByteArray, bytes]):
    """
    Equivalent to `List(byte, size)` but more convenient & efficient.

    When encoding a series of bytes, List(byte, ...) requires an awkward input
    shaped like: ``(b'A', b'B', b'C')``. `ByteList` accepts a simple
    :class:`bytes` object like ``b'ABC'`` for encoding.
    """

    def __init__(self, max_length: int) -> None:
        super().__init__(element_sedes=byte, max_length=max_length)

    def serialize(self, value: BytesOrByteArray) -> bytes:
        if len(value) > self.max_length:
            raise SerializationError(
                f"Cannot serialize length {len(value)} byte-string as ByteList{self.length}"
            )

        return value

    def serialize_element_for_tree(self, index: int, byte_value: int) -> bytes:
        if not 0 <= byte_value < 256:
            raise SerializationError(
                f"Cannot serialize byte as its value {byte_value} is invalid"
            )

        return bytes((byte_value,))

    def deserialize(self, data: bytes) -> bytes:
        if len(data) > self.max_length:
            raise DeserializationError(
                f"Cannot deserialize length {len(data)} data as ByteList{self.length}"
            )
        return data

    def get_hash_tree_root(self, value: bytes) -> bytes:
        serialized_value = self.serialize(value)
        merkle_leaves = pack_bytes(serialized_value)
        merkleized = merkleize(merkle_leaves, limit=self.chunk_count)
        return mix_in_length(merkleized, len(value))

    def get_sedes_id(self) -> str:
        return f"{self.__class__.__name__}{self.length}"
