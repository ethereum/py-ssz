from typing import (
    Union,
)

from ssz.sedes.base import (
    CompositeSedes,
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


byte_list = ByteList()
