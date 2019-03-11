import collections

from ssz.constants import (
    LENGTH_PREFIX_SIZE,
    MAX_CONTENT_LENGTH,
)
from ssz.exceptions import (
    SerializationError,
)


def get_length_prefix(content: bytes) -> bytes:
    return len(content).to_bytes(LENGTH_PREFIX_SIZE, "little")


def validate_content_length(content: bytes) -> None:
    if len(content) >= MAX_CONTENT_LENGTH:
        raise SerializationError(
            f"Content is too big to be encoded in prefix of {LENGTH_PREFIX_SIZE} bytes",
        )


def get_duplicates(values):
    counts = collections.Counter(values)
    return tuple(
        item
        for item, num in counts.items()
        if num > 1
    )
