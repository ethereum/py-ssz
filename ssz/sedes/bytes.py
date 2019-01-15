from typing import (
    Union,
)

from ssz.sedes.base import (
    LengthPrefixedSedes,
)
from ssz.tree_hash.hash_eth2 import (
    hash_eth2,
)

BytesOrByteArray = Union[bytes, bytearray]


class Bytes(LengthPrefixedSedes[BytesOrByteArray, bytes]):

    length_bytes = 4

    def serialize_content(self, value: BytesOrByteArray) -> bytes:
        return value

    def deserialize_content(self, content: bytes) -> bytes:
        return content

    def intermediate_tree_hash(self, value: BytesOrByteArray) -> bytes:
        return hash_eth2(self.serialize(value))


bytes_sedes = Bytes()
