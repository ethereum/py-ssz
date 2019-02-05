from typing import (
    Any,
    Sequence,
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
        chunks_unpadded = (
            b''.join(input_items[i:i + items_per_chunk])
            for i in range(0, len(input_items), items_per_chunk)
        )
        chunks = tuple(
            chunk.ljust(SSZ_CHUNK_SIZE, b"\x00")
            for chunk in chunks_unpadded
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
