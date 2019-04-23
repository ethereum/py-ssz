from eth_utils import (
    decode_hex,
    encode_hex,
)

from ssz.sedes.base import (
    BasicSedes,
)


class Byte(BasicSedes[bytes, bytes]):
    def __init__(self) -> None:
        super().__init__(1)

    def serialize_content(self, value: bytes) -> bytes:
        return value

    def deserialize_content(self, content: bytes) -> bytes:
        return content

    def serialize_text(self, value: bytes) -> str:
        return encode_hex(value)

    def deserialize_text(self, content: str) -> bytes:
        return decode_hex(content)


byte = Byte()
