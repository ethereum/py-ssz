import collections
from collections.abc import (
    Iterable,
    Sequence,
)
from typing import (
    Any,
)

from eth_hash.auto import (
    keccak,
)
from eth_typing import (
    Hash32,
)

from ssz.constants import (
    SSZ_CHUNK_SIZE,
)

from ssz.sedes import (
    BaseSedes,
    List,
    boolean,
    bytes_sedes,
    empty_list,
)


def infer_list_sedes(value):
    if len(value) == 0:
        return empty_list
    else:
        try:
            element_sedes = infer_sedes(value[0])
        except TypeError:
            raise TypeError("Could not infer sedes for list elements")
        else:
            return List(element_sedes)


def infer_sedes(value):
    """
    Try to find a sedes objects suitable for a given Python object.
    """
    if isinstance(value.__class__, BaseSedes):
        # Mainly used for `Serializable` Classes
        return value.__class__

    elif isinstance(value, bool):
        return boolean

    elif isinstance(value, int):
        raise TypeError("uint sedes object or uint string needs to be specified for ints")

    elif isinstance(value, (bytes, bytearray)):
        return bytes_sedes

    elif isinstance(value, Sequence):
        return infer_list_sedes(value)

    elif isinstance(value, Iterable):
        raise TypeError("Cannot infer list sedes for iterables that are not sequences")

    else:
        raise TypeError(f"Did not find sedes handling type {type(value).__name__}")


def get_duplicates(values):
    counts = collections.Counter(values)
    return tuple(
        item
        for item, num in counts.items()
        if num > 1
    )


def hash_eth2(data: bytes) -> Hash32:
    """
    Return Keccak-256 hashed result.
    Note: it's a placeholder and we aim to migrate to a S[T/N]ARK-friendly hash function in
    a future Ethereum 2.0 deployment phase.
    """
    return keccak(data)


def merkle_hash(input_items: Sequence[Any]) -> Hash32:
    """
    Merkle tree hash of a list of homogenous, non-empty items
    """

    # Store length of list (to compensate for non-bijectiveness of padding)
    data_length = len(input_items).to_bytes(32, "little")

    if len(input_items) == 0:
        # Handle empty list case
        chunks = (b'\x00' * SSZ_CHUNK_SIZE,)
    elif len(input_items[0]) < SSZ_CHUNK_SIZE:
        # See how many items fit in a chunk
        items_per_chunk = SSZ_CHUNK_SIZE // len(input_items[0])

        # Build a list of chunks based on the number of items in the chunk
        chunks = tuple(
            b''.join(input_items[i:i + items_per_chunk])
            for i in range(0, len(input_items), items_per_chunk)
        )
    else:
        # Leave large items alone
        chunks = input_items

    # Tree-hash
    while len(chunks) > 1:
        if len(chunks) % 2 == 1:
            chunks += (b'\x00' * SSZ_CHUNK_SIZE, )
        chunks = tuple(
            hash_eth2(chunks[i] + chunks[i + 1])
            for i in range(0, len(chunks), 2)
        )

    # Return hash of root and length data
    return hash_eth2(chunks[0] + data_length)
