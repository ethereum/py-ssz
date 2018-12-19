from typing import (
    Any,
    Sequence,
)

from eth_typing import (
    Hash32,
)

from .hash_eth2 import (
    hash_eth2,
)


def merkle_hash(input_items: Sequence[Any], chunk_size: int=128) -> Hash32:
    """
    Merkle tree hash of a list of homogenous, non-empty items
    """

    data_length = len(input_items).to_bytes(32, 'big')

    if len(input_items) == 0:
        chunks = (b'\x00' * chunk_size,)
    elif len(input_items[0]) < chunk_size:
        items_per_chunk = chunk_size // len(input_items[0])

        chunks = tuple(
            b''.join(input_items[i:i + items_per_chunk])
            for i in range(0, len(input_items), items_per_chunk)
        )
    else:
        chunks = input_items

    while len(chunks) > 1:
        if len(chunks) % 2 == 1:
            chunks += (b'\x00' * chunk_size, )
        chunks = tuple(
            hash_eth2(chunks[i] + chunks[i + 1])
            for i in range(0, len(chunks), 2)
        )
    return hash_eth2(chunks[0] + data_length)
