from typing import Any

from eth_utils import encode_hex

from ssz.exceptions import DeserializationError
from ssz.sedes.basic import BasicSedes


class Boolean(BasicSedes[bool, bool]):
    def __init__(self) -> None:
        super().__init__(size=1)

    def serialize(self, value: bool) -> bytes:
        if value is False:
            return b"\x00"
        elif value is True:
            return b"\x01"
        else:
            raise TypeError(f"Can only serialize bools, got {type(value)}")

    def deserialize(self, data: bytes) -> bool:
        if data == b"\x00":
            return False
        elif data == b"\x01":
            return True
        else:
            raise DeserializationError(
                f"Invalid serialized boolean (must be either 0x01 or 0x00, got "
                f"{encode_hex(data)})"
            )

    def get_sedes_id(self) -> str:
        return self.__class__.__name__

    def __hash__(self) -> int:
        return hash((hash(Boolean),))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Boolean)


class Bit(Boolean):
    pass


boolean = Boolean()
