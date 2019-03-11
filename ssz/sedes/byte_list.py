from typing import (
    Union,
)

from ssz.hash import (
    hash_eth2,
)
from ssz.sedes.base import (
    LengthPrefixedSedes,
)

BytesOrByteArray = Union[bytes, bytearray]


class ByteList(LengthPrefixedSedes[BytesOrByteArray, bytes]):

    is_variable_length = True

    def get_fixed_length(self):
        raise ValueError("byte list has no fixed length")

    def serialize_content(self, value: BytesOrByteArray) -> bytes:
        return value

    def deserialize_content(self, content: bytes) -> bytes:
        return content

    def intermediate_tree_hash(self, value: BytesOrByteArray) -> bytes:
        return hash_eth2(self.serialize(value))


byte_list = ByteList()
