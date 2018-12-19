from .merkle_hash import merkle_hash
from .hash_eth2 import hash_eth2
from ssz.exceptions import TreeHashException
from ssz.utils import infer_sedes
from ssz.sedes import (
    boolean,
    uint8,
    uint16,
    uint24,
    uint32,
    uint40,
    uint48,
    uint56,
    uint64,
    uint128,
    uint256,
    uint384,
    uint512,
    address,
    hash32,
)

just_serialize = tuple(
    map(
        type,
        (
            boolean,
            uint8,
            uint16,
            uint24,
            uint32,
            uint40,
            uint48,
            uint56,
            uint64,
            uint128,
            uint256,
            address,
            hash32,
        )
    )
)

serialize_then_hash = tuple(
    map(
        type,
        (
            uint384,
            uint512,
        )
    )
)


def hash_tree_root(obj, sedes=None):
    if sedes is None:
        sedes = infer_sedes(obj)
    if isinstance(sedes, just_serialize):
        return sedes.serialize(obj).ljust(32, b'\x00')
    elif isinstance(sedes, serialize_then_hash):
        return hash_eth2(sedes.serialize(obj))

    if isinstance(obj, list):
        return merkle_hash(hash_tree_root(item) for item in obj)

    # TODO: check container type

    raise TreeHashException("Can't produce tree hash", obj, sedes)
