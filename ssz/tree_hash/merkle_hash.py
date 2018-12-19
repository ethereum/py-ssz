from typing import (
    Sequence,
)

from .hash_eth2 import (
    hash_eth2,
)


def merkle_hash(items: Sequence, chunk_size=128):
    """
    Merkle tree hash of a list of homogenous, non-empty items
    """

    # Store length of list (to compensate for non-bijectiveness of padding)
    datalen = len(items).to_bytes(32, 'big')

    if len(items) == 0:
        # Handle empty list case
        chunkz = [b'\x00' * chunk_size]
    elif len(items[0]) < chunk_size:
        # See how many items fit in a chunk
        items_per_chunk = chunk_size // len(items[0])

        # Build a list of chunks based on the number of items in the chunk
        chunkz = [b''.join(items[i:i + items_per_chunk])
                  for i in range(0, len(items), items_per_chunk)]
    else:
        # Leave large items alone
        chunkz = items

    # Tree-hash
    while len(chunkz) > 1:
        if len(chunkz) % 2 == 1:
            chunkz.append(b'\x00' * chunk_size)
        chunkz = [hash_eth2(chunkz[i] + chunkz[i + 1]) for i in range(0, len(chunkz), 2)]

    # Return hash of root and length data
    return hash_eth2(chunkz[0] + datalen)
