from typing import (
    Union,
)

from eth_utils import (
    encode_hex,
)

from ssz.exceptions import (
    SerializationError,
)
from ssz.sedes.base import (
    FixedSizedSedes,
)

BytesOrByteArray = Union[bytes, bytearray]


class Hash(FixedSizedSedes[BytesOrByteArray, bytes]):

    def serialize_content(self, value: BytesOrByteArray) -> bytes:
        if len(value) != self.length:
            raise SerializationError(
                f"Can only serialize values of exactly {len(value)} bytes, got"
                f"{encode_hex(value)} which is {len(value)} bytes."
            )

        return value

    def deserialize_content(self, content: bytes) -> bytes:
        return content


hash32 = Hash(32)
address = Hash(20)
