from ssz.exceptions import (
    DeserializationError,
    SerializationError,
)
from ssz.sedes.base import (
    BasicSedes,
)


class Byte(BasicSedes[bytes, bytes]):
    size = 1

    def __init__(self) -> None:
        super().__init__(1)

    def serialize(self, value: bytes) -> bytes:
        if len(value) != 1:
            raise SerializationError(
                f"The `Byte` sedes can only serialize single bytes.  Got: {value!r}"
            )
        return value

    def deserialize(self, data: bytes) -> bytes:
        if len(data) != 1:
            raise DeserializationError(
                f"The `Byte` sedes can only deserialize single bytes.  Got: {data!r}"
            )
        return data


byte = Byte()
