from typing import Any

from eth_typing import Hash32

from ssz.sedes import infer_sedes
from ssz.sedes.base import BaseSedes


def get_hash_tree_root(value: Any, sedes: BaseSedes = None) -> Hash32:
    if sedes is None:
        sedes = infer_sedes(value)

    return sedes.get_hash_tree_root(value)
