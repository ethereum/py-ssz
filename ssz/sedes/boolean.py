from eth_utils import (
    encode_hex,
)

from ssz.exceptions import (
    DeserializationError,
)
from ssz.sedes.base import (
    BasicSedes,
)


class Boolean(BasicSedes[bool, bool]):

    def __init__(self) -> None:
        super().__init__(size=1)

    def serialize_content(self, value: bool) -> bytes:
        if value is False:
            return b"\x00"
        elif value is True:
            return b"\x01"
        else:
            raise TypeError(f"Can only serialize bools, got {type(value)}")

    def deserialize_content(self, content: bytes) -> bool:
        if content == b"\x00":
            return False
        elif content == b"\x01":
            return True
        else:
            raise DeserializationError(
                f"Invalid serialized boolean (must be either 0x01 or 0x00, got "
                f"{encode_hex(content)})",
            )


boolean = Boolean()
