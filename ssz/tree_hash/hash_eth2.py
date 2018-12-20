from eth_hash.auto import (
    keccak,
)
from eth_typing import (
    Hash32,
)


def hash_eth2(data: bytes) -> Hash32:
    """
    Return Keccak-256 hashed result.
    Note: it's a placeholder and we aim to migrate to a S[T/N]ARK-friendly hash function in
    a future Ethereum 2.0 deployment phase.
    """
    return keccak(data)
