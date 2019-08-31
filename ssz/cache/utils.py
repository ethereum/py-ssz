import functools
from typing import (
    Any,
    Iterable,
)

from eth_typing import (
    Hash32,
)
from eth_utils import (
    to_tuple,
)

from ssz.sedes.base import (
    TSedes,
)
from ssz.typing import (
    CacheObj,
)


def get_key(sedes: TSedes, value: Any) -> str:
    key = _get_key(sedes, value).hex()
    sedes_name = type(sedes).__name__
    if len(key) > 0:
        return sedes_name + key
    else:
        # If the serialized result is empty, use sedes name as the key
        if hasattr(sedes, 'element_sedes'):
            return f"{sedes_name}[{sedes.max_length}]({type(sedes.element_sedes).__name__})"
        else:
            return sedes_name


@functools.lru_cache(maxsize=2**12)
def _get_key(sedes: TSedes, value: Any) -> bytes:
    return sedes.serialize(value)


@to_tuple
def get_merkle_leaves_without_cache(value: Any, element_sedes: TSedes) -> Iterable[Hash32]:
    for element in value:
        yield element_sedes.get_hash_tree_root(element)


@to_tuple
def get_merkle_leaves_with_cache(value: Any,
                                 element_sedes: TSedes,
                                 cache: CacheObj) -> Iterable[Hash32]:
    """
    NOTE: cache is mutable
    """
    for element in value:
        key = element_sedes.get_key(element)
        if key not in cache:
            root, cache = (
                element_sedes.get_hash_tree_root_and_leaves(
                    element,
                    cache,
                )
            )
            cache[key] = root
        yield cache[key]
