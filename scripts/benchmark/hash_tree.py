from contextlib import contextmanager
from itertools import chain
import random
import time

from ssz.hash_tree import HashTree
from ssz.utils import merkleize_with_cache

NUM_CHUNKS = 1000000
NUM_UPDATES = 100


def get_random_chunk():
    return bytes(random.randint(0, 255) for _ in range(32))


@contextmanager
def benchmark(message):
    start_time = time.time()
    yield
    end_time = time.time()
    print(message, f"{end_time - start_time} s")


if __name__ == "__main__":
    with benchmark(f"Preparing {NUM_CHUNKS} chunks"):
        chunks = [get_random_chunk() for _ in range(NUM_CHUNKS)]
        update_indices = random.sample(list(range(NUM_CHUNKS)), NUM_UPDATES)

    print()
    print("-- Merkleize --")
    cache = {}
    with benchmark(f"First root access"):
        merkleize_with_cache(chunks, cache)

    with benchmark(f"Second root access"):
        merkleize_with_cache(chunks, cache)

    for update_index in update_indices:
        chunks[update_index] = get_random_chunk()
    with benchmark(f"Update and root access"):
        merkleize_with_cache(chunks, cache)

    print()
    print("-- Hash tree -- ")

    with benchmark(f"First root access"):
        hash_tree = HashTree.compute(chunks)
        hash_tree.root

    with benchmark(f"Second root access"):
        hash_tree.root

    with benchmark(f"Update and root access"):
        updates = chain(
            *((update_index, get_random_chunk()) for update_index in update_indices)
        )

        updated_hash_tree = hash_tree.mset(*updates)
        updated_hash_tree.root
