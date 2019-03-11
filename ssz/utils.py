import collections
from itertools import (
    count,
    dropwhile,
)
import math
from typing import (
    Sequence,
    Tuple,
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
    LENGTH_PREFIX_SIZE,
    MAX_CONTENT_LENGTH,
)
from ssz.exceptions import (
    SerializationError,
)
from ssz.hash import (
    hash_eth2,
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


def get_items_per_chunk(item_size: int) -> int:
    if item_size <= 0:
        raise ValueError("Item size must be positive integer")
    elif CHUNK_SIZE % item_size != 0:
        raise ValueError("Item size must be a divisor of chunk size")
    elif item_size <= CHUNK_SIZE:
        return CHUNK_SIZE // item_size
    else:
        raise Exception("Invariant: unreachable")


def pack(serialized_values: Sequence[bytes]) -> Tuple[bytes]:
    if len(serialized_values) == 0:
        return (EMPTY_CHUNK,)

    item_size = len(serialized_values[0])
    items_per_chunk = get_items_per_chunk(item_size)

    number_of_items = len(serialized_values)
    number_of_chunks = (number_of_items + (items_per_chunk - 1)) // items_per_chunk

    chunk_partitions = partition(items_per_chunk, serialized_values, pad=b"")
    chunks_unpadded = (b"".join(chunk_partition) for chunk_partition in chunk_partitions)

    full_chunks = tuple(take(number_of_chunks - 1, chunks_unpadded))
    last_chunk = first(chunks_unpadded)
    if len(tuple(chunks_unpadded)) > 0:
        raise Exception("Invariant: all chunks have been taken")

    return full_chunks + (last_chunk.ljust(CHUNK_SIZE, b"\x00"),)


def get_next_power_of_two(integer: int) -> int:
    powers_of_two = (2**exponent for exponent in count(0))
    greater_or_equal_powers = dropwhile(lambda power: power < integer, powers_of_two)
    return first(greater_or_equal_powers)


def pad_chunks(chunks: Sequence[bytes]) -> Tuple[bytes]:
    unpadded_number_of_chunks = len(chunks)
    padded_number_of_chunks = get_next_power_of_two(unpadded_number_of_chunks)
    padding = (EMPTY_CHUNK,) * (padded_number_of_chunks - unpadded_number_of_chunks)
    return tuple(chunks) + padding


def hash_layer(child_layer: Sequence[bytes]) -> Tuple[bytes]:
    child_pairs = partition(2, child_layer)
    parent_layer = tuple(
        hash_eth2(left_child + right_child)
        for left_child, right_child in child_pairs
    )
    return parent_layer


def merkleize(chunks: Sequence[bytes]) -> bytes:
    padded_chunks = pad_chunks(chunks)
    number_of_layers = int(math.log2(len(padded_chunks))) + 1

    layers = take(number_of_layers, iterate(hash_layer, padded_chunks))
    root_layer = last(layers)
    if not len(root_layer) == 1:
        raise Exception("Invariant: root level of merkle tree has single element")
    return root_layer[0]


def mix_in_length(root: bytes, length: int) -> bytes:
    return hash_eth2(root + length.to_bytes(CHUNK_SIZE, "little"))
