from typing import (
    Union,
)

from ssz.utils import (
    merkleize,
    pack,
)
from ssz.sedes.base import (
    CompositeSedes,
)

BytesOrByteArray = Union[bytes, bytearray]


class ByteList(CompositeSedes[BytesOrByteArray, bytes]):

    is_variable_length = True

    def get_fixed_length(self):
        raise ValueError("byte list has no fixed length")

    def serialize_content(self, value: BytesOrByteArray) -> bytes:
        return value

    def deserialize_content(self, content: bytes) -> bytes:
        return content

    def hash_tree_root(self, value: bytes) -> bytes:
        serialized_value = value
        return merkleize(pack((serialized_value,)))


byte_list = ByteList()
