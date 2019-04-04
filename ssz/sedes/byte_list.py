from typing import (
    Union,
)

from ssz.sedes.base import (
    BaseCompositeSedes,
)
from ssz.utils import (
    merkleize,
    mix_in_length,
    pack_bytes,
)

BytesOrByteArray = Union[bytes, bytearray]


class ByteList(BaseCompositeSedes[BytesOrByteArray, bytes]):

    is_fixed_sized = False

    def get_fixed_size(self):
        raise ValueError("byte list has no static size")

    def serialize(self, value: BytesOrByteArray) -> bytes:
        return value

    def deserialize(self, data: bytes) -> bytes:
        return data

    def hash_tree_root(self, value: bytes) -> bytes:
        merkle_leaves = pack_bytes(value)
        merkleized = merkleize(merkle_leaves)
        return mix_in_length(merkleized, len(value))


byte_list = ByteList()
