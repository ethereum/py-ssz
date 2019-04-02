import collections
import math
from typing import (
    Sequence,
    Tuple,
)

from eth_typing import (
    Hash32,
)
from eth_utils.toolz import (
    first,
    iterate,
    last,
    partition,
    take,
)

from ssz.constants import (
    CHUNK_SIZE,
    EMPTY_CHUNK,
    MAX_CONTENT_SIZE,
    SIZE_PREFIX_SIZE,
)
from ssz.exceptions import (
    SerializationError,
)
from ssz.hash import (
    hash_eth2,
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


def get_items_per_chunk(item_size: int) -> int:
    if item_size < 0:
        raise ValueError("Item size must be positive integer")
    elif item_size == 0:
        return 1
    elif CHUNK_SIZE % item_size != 0:
        raise ValueError("Item size must be a divisor of chunk size")
    elif item_size <= CHUNK_SIZE:
        return CHUNK_SIZE // item_size
    else:
        raise Exception("Invariant: unreachable")


def pack(serialized_values: Sequence[bytes]) -> Tuple[Hash32, ...]:
    if len(serialized_values) == 0:
        return (EMPTY_CHUNK,)

    item_size = len(serialized_values[0])
    items_per_chunk = get_items_per_chunk(item_size)

    number_of_items = len(serialized_values)
    number_of_chunks = (number_of_items + (items_per_chunk - 1)) // items_per_chunk

    chunk_partitions = partition(items_per_chunk, serialized_values, pad=b"")
    chunks_unpadded = (b"".join(chunk_partition) for chunk_partition in chunk_partitions)

    full_chunks = tuple(Hash32(chunk) for chunk in take(number_of_chunks - 1, chunks_unpadded))
    last_chunk = first(chunks_unpadded)
    if len(tuple(chunks_unpadded)) > 0:
        raise Exception("Invariant: all chunks have been taken")

    return full_chunks + (Hash32(last_chunk.ljust(CHUNK_SIZE, b"\x00")),)


def pack_bytes(byte_string: bytes) -> Tuple[Hash32]:
    size = len(byte_string)
    if size == 0:
        return (EMPTY_CHUNK,)

    number_of_full_chunks = size // CHUNK_SIZE
    last_chunk_is_full = size % CHUNK_SIZE == 0

    full_chunks = tuple(
        byte_string[chunk_index * CHUNK_SIZE:(chunk_index + 1) * CHUNK_SIZE]
        for chunk_index in range(number_of_full_chunks)
    )
    if last_chunk_is_full:
        return full_chunks
    else:
        last_chunk = byte_string[number_of_full_chunks * CHUNK_SIZE:].ljust(CHUNK_SIZE, b"\x00")
        return full_chunks + (last_chunk,)


def get_next_power_of_two(value: int) -> int:
    if value <= 0:
        return 1
    else:
        return 2**(value - 1).bit_length()


def pad_chunks(chunks: Sequence[Hash32]) -> Tuple[Hash32, ...]:
    unpadded_number_of_chunks = len(chunks)
    padded_number_of_chunks = get_next_power_of_two(unpadded_number_of_chunks)
    padding = (EMPTY_CHUNK,) * (padded_number_of_chunks - unpadded_number_of_chunks)
    return tuple(chunks) + padding


def hash_layer(child_layer: Sequence[bytes]) -> Tuple[Hash32, ...]:
    if len(child_layer) % 2 != 0:
        raise ValueError("Layer must have an even number of elements")

    child_pairs = partition(2, child_layer)
    parent_layer = tuple(
        hash_eth2(left_child + right_child)
        for left_child, right_child in child_pairs
    )
    return parent_layer


def merkleize(chunks: Sequence[Hash32]) -> Hash32:
    padded_chunks = pad_chunks(chunks)
    number_of_layers = int(math.log2(len(padded_chunks))) + 1

    layers = take(number_of_layers, iterate(hash_layer, padded_chunks))
    root, = last(layers)
    return root


def mix_in_length(root: Hash32, length: int) -> Hash32:
    return hash_eth2(root + length.to_bytes(CHUNK_SIZE, "little"))
