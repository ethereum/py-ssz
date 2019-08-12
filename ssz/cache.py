import functools

from eth_utils import (
    to_tuple,
)


def get_key(sedes, value):
    key = _get_key(sedes, value).hex()
    if len(key) > 0:
        sedes_name = type(sedes).__name__
        return sedes_name + _get_key(sedes, value).hex()
    else:
        return key


@functools.lru_cache(maxsize=2**30)
def _get_key(sedes, value):
    return sedes.serialize(value)


@to_tuple
def get_merkle_leaves_without_cache(value, element_sedes):
    for element in value:
        yield element_sedes.get_hash_tree_root(element)


@to_tuple
def get_merkle_leaves_with_cache(value, element_sedes, db):
    """
    NOTE: db is mutable
    """
    for element in value:
        key = element_sedes.get_key(element)
        if key not in db or len(key) == 0:
            root, db = (
                element_sedes.get_hash_tree_root_and_leaves(
                    element,
                    db,
                )
            )
            db[key] = root
        yield db[key]
