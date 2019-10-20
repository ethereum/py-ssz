import functools
from typing import Any, Iterable

from eth_typing import Hash32
from eth_utils import to_tuple

from ssz.sedes.base import TSedes
from ssz.typing import CacheObj


def get_key(sedes, value: Any) -> str:
    key = get_base_key(sedes, value).hex()
    if len(key) == 0:
        key = ""
    return f"{sedes.get_sedes_id()}{key}"


@functools.lru_cache(maxsize=2 ** 12)
def get_base_key(sedes: TSedes, value: Any) -> bytes:
    return sedes.serialize(value)


@to_tuple
def get_merkle_leaves_without_cache(
    value: Any, element_sedes: TSedes
) -> Iterable[Hash32]:
    for element in value:
        yield element_sedes.get_hash_tree_root(element)


@to_tuple
def get_merkle_leaves_with_cache(
    value: Any, element_sedes: TSedes, cache: CacheObj
) -> Iterable[Hash32]:
    """
    NOTE: cache is mutable
    """
    for element in value:
        key = element_sedes.get_key(element)
        if key not in cache:
            root, cache = element_sedes.get_hash_tree_root_and_leaves(element, cache)
            cache[key] = root
        yield cache[key]
