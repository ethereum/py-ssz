from typing import (
    Union,
)

from ssz.sedes.base import (
    CompositeSedes,
)
from ssz.utils import (
    merkleize,
    pack,
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
        serialized_value = value
        return merkleize(pack((serialized_value,)))


byte_list = ByteList()
