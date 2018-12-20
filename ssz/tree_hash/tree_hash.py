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
    Hash,
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
    if sedes is None:
        sedes = infer_sedes(input_object)

    if isinstance(sedes, (Boolean, Hash, UnsignedInteger)):
        serialization = sedes.serialize(input_object)
        if isinstance(sedes, UnsignedInteger) and sedes.num_bytes > 32:
            return hash_eth2(serialization)
        else:
            return serialization.ljust(32, b'\x00')

    if isinstance(input_object, abc.Iterable):
        return merkle_hash([hash_tree_root(item, sedes.element_sedes) for item in input_object])

    # TODO: check container type

    raise TreeHashException("Can't produce tree hash", input_object, sedes)
