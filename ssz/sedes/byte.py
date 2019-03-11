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


byte = Byte()
