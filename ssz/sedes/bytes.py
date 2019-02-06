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


class Bytes(LengthPrefixedSedes[BytesOrByteArray, bytes]):

    length_bytes = 4

    def serialize_content(self, value: BytesOrByteArray) -> bytes:
        return value

    def deserialize_content(self, content: bytes) -> bytes:
        return content

    def intermediate_tree_hash(self, value: BytesOrByteArray, cache=True) -> bytes:
        return hash_eth2(self.serialize(value))


bytes_sedes = Bytes()
