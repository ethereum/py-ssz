from collections import (
    abc,
)
from typing import (
    Any,
)

from eth_typing import (
    Hash32,
)

from ssz.exceptions import (
    TreeHashException,
)
from ssz.sedes import (
    Boolean,
    Bytes,
    Hash,
    Serializable,
    UnsignedInteger,
)
from ssz.utils import (
    infer_sedes,
)

from .hash_eth2 import (
    hash_eth2,
)
from .merkle_hash import (
    merkle_hash,
)


def hash_tree_root(input_object: Any, sedes: Any=None) -> Hash32:
    result = _hash_tree_root(input_object, sedes)
    if len(result) < 32:
        return Hash32(result.ljust(32, b'\x00'))
    return Hash32(result)


def _hash_tree_root(input_object: Any, sedes: Any=None) -> bytes:
    if sedes is None:
        sedes = infer_sedes(input_object)

    if isinstance(sedes, (Boolean, Hash)):
        return sedes.serialize(input_object)

    if isinstance(sedes, UnsignedInteger):
        value = input_object.to_bytes(sedes.num_bytes, 'big')
        if sedes.num_bytes > 32:
            return hash_eth2(value)
        else:
            return value

    if isinstance(sedes, Bytes):
        return hash_eth2(sedes.serialize(input_object))

    if isinstance(input_object, Serializable):
        container_hashs = (
            _hash_tree_root(input_object[field_name], field_sedes)
            for field_name, field_sedes in input_object._meta.fields
        )
        return hash_eth2(b''.join(container_hashs))

    if isinstance(input_object, abc.Iterable):
        input_items = tuple(_hash_tree_root(item, sedes.element_sedes) for item in input_object)
        return merkle_hash(input_items)

    raise TreeHashException("Can't produce tree hash", input_object, sedes)
