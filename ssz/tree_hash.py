from typing import (
    Any,
)

from eth_typing import (
    Hash32,
)

from ssz.utils import (
    infer_sedes
)
from ssz.sedes import (
    BaseSedes,
)


def hash_tree_root(value: Any, sedes: BaseSedes=None) -> Hash32:
    if sedes is None:
        sedes = infer_sedes(value)

    intermediate_tree_hash = sedes.intermediate_tree_hash(value)

    if len(intermediate_tree_hash) < 32:
        return Hash32(intermediate_tree_hash.ljust(32, b'\x00'))
    else:
        return Hash32(intermediate_tree_hash)
