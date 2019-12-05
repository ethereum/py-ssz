import functools
import hashlib

from eth_typing import Hash32


@functools.lru_cache(maxsize=2 ** 12)
def hash_eth2(data: bytes) -> Hash32:
    """
    Return SHA-256 hashed result.
    Note: it's a placeholder and we aim to migrate to a S[T/N]ARK-friendly hash function in
    a future Ethereum 2.0 deployment phase.
    """
    return Hash32(hashlib.sha256(data).digest())
