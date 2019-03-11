from typing import (
    Union,
)

from ssz.exceptions import (
    SerializationError,
)
from ssz.sedes.tuple import (
    CompositeSedes,
)

BytesOrByteArray = Union[bytes, bytearray]


class ByteTuple(CompositeSedes[BytesOrByteArray, bytes]):

    def __init__(self, length: int) -> None:
        self.length = length

    def serialize_content(self, value: BytesOrByteArray) -> bytes:
        if len(value) != self.length:
            raise SerializationError(
                f"Cannot serialize {len(value)} elements as bytes{self.length}"
            )

        return value

    #
    # Deserialization
    #
    def deserialize_content(self, content: bytes) -> bytes:
        return content

    #
    # Size
    #
    is_variable_length = False

    def get_fixed_length(self):
        return self.length

    #
    # Tree hashing
    #
    def intermediate_tree_hash(self, value: BytesOrByteArray) -> bytes:
        pass  # TODO


# Use case: for hashes and messages
bytes32 = ByteTuple(32)
# Use case: for BLS public keys
bytes48 = ByteTuple(48)
# Use case: for BLS signatures
bytes96 = ByteTuple(96)
