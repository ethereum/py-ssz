from typing import (
    TYPE_CHECKING,
    Any,
)

from eth_typing import (
    Hash32,
)

from ssz.utils import (
    infer_sedes,
)

if TYPE_CHECKING:
    from ssz.sedes.base import (  # noqa: F401
        BaseSedes,
    )


def hash_tree_root(value: Any, sedes: 'BaseSedes'=None, cache=True) -> Hash32:
    if sedes is None:
        sedes = infer_sedes(value)

    intermediate_tree_hash = sedes.intermediate_tree_hash(value, cache)

    if len(intermediate_tree_hash) < 32:
        return Hash32(intermediate_tree_hash.ljust(32, b'\x00'))
    else:
        return Hash32(intermediate_tree_hash)
