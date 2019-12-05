from typing import Any

from ssz.exceptions import DeserializationError, SerializationError
from ssz.sedes.basic import BasicSedes


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

    def get_sedes_id(self) -> str:
        return self.__class__.__name__

    def __hash__(self) -> int:
        return hash((Byte,))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Byte)


byte = Byte()
