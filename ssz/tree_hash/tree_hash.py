from .merkle_hash import merkle_hash
from .hash_eth2 import hash_eth2
from ssz.exceptions import TreeHashException
from ssz.utils import infer_sedes
from ssz.sedes import (
    Boolean,
    Hash,
    UnsignedInteger,
)


def hash_tree_root(obj, sedes=None):
    if sedes is None:
        sedes = infer_sedes(obj)

    if isinstance(sedes, (Boolean, Hash, UnsignedInteger)):
        serialization = sedes.serialize(obj)
        if isinstance(sedes, UnsignedInteger) and sedes.num_bytes > 32:
            return hash_eth2(serialization)
        else:
            return serialization.ljust(32, b'\x00')

    if isinstance(obj, list):
        return merkle_hash([hash_tree_root(item, sedes.element_sedes) for item in obj])

    # TODO: check container type

    raise TreeHashException("Can't produce tree hash", obj, sedes)
