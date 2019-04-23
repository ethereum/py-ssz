from typing import (
    Union,
)

from eth_utils import (
    decode_hex,
    encode_hex,
)

from ssz.sedes.base import (
    CompositeSedes,
)
from ssz.utils import (
    merkleize,
    mix_in_length,
    pack_bytes,
)

BytesOrByteArray = Union[bytes, bytearray]


class ByteList(CompositeSedes[BytesOrByteArray, bytes]):
    is_static_sized = False

    def get_static_size(self):
        raise ValueError("byte list has no static size")

    def serialize_content(self, value: BytesOrByteArray) -> bytes:
        return value

    def deserialize_content(self, content: bytes) -> bytes:
        return content

    def hash_tree_root(self, value: bytes) -> bytes:
        merkle_leaves = pack_bytes(value)
        merkleized = merkleize(merkle_leaves)
        return mix_in_length(merkleized, len(value))

    def serialize_text(self, value: bytes) -> str:
        return encode_hex(value)

    def deserialize_text(self, content: str) -> bytes:
        return decode_hex(content)


byte_list = ByteList()
