from eth_typing import (
    Hash32,
)

CHUNK_SIZE = 32  # named BYTES_PER_CHUNK in the spec
EMPTY_CHUNK = Hash32(b"\x00" * CHUNK_SIZE)

SIGNATURE_FIELD_NAME = "signature"

# number of bytes for a serialized offset
OFFSET_SIZE = 4
