from typing import (
    Union,
)

from ssz.sedes.base import LengthPrefixedSedes


BytesOrByteArray = Union[bytes, bytearray]


class Bytes(LengthPrefixedSedes[BytesOrByteArray, bytes]):

    length_bytes = 4

    def serialize_content(self, value: BytesOrByteArray) -> bytes:
        return value

    def deserialize_content(self, content: bytes) -> bytes:
        return content


bytes_sedes = Bytes()
