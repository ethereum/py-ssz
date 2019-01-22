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


class BytesN(FixedSizedSedes[BytesOrByteArray, bytes]):

    def serialize_content(self, value: BytesOrByteArray) -> bytes:
        if len(value) != self.length:
            raise SerializationError(
                f"Can only serialize values of exactly {self.length} bytes, got"
                f"{encode_hex(value)} which is {len(value)} bytes."
            )
        return value

    def deserialize_content(self, content: bytes) -> bytes:
        return content


# Use case: for hashes and messages
bytes32 = BytesN(32)
# Use case: for BLS public keys
bytes48 = BytesN(48)
# Use case: for BLS signatures
bytes96 = BytesN(96)
