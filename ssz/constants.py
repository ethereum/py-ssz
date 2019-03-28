from eth_typing import (
    Hash32,
)

CHUNK_SIZE = 32  # named BYTES_PER_CHUNK in the spec
EMPTY_CHUNK = Hash32(b"\x00" * CHUNK_SIZE)

SIZE_PREFIX_SIZE = 4  # named BYTES_PER_LENGTH_PREFIX in the spec
MAX_CONTENT_SIZE = 2 ** (SIZE_PREFIX_SIZE * 8) - 1
