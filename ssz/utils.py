import collections

from ssz.constants import (
    MAX_CONTENT_SIZE,
    SIZE_PREFIX_SIZE,
)
from ssz.exceptions import (
    SerializationError,
)


def get_duplicates(values):
    counts = collections.Counter(values)
    return tuple(
        item
        for item, num in counts.items()
        if num > 1
    )


def get_size_prefix(content: bytes) -> bytes:
    return len(content).to_bytes(SIZE_PREFIX_SIZE, "little")


def validate_content_size(content: bytes) -> None:
    if len(content) >= MAX_CONTENT_SIZE:
        raise SerializationError(
            f"Content size is too large to be encoded in a {SIZE_PREFIX_SIZE} byte prefix",
        )
