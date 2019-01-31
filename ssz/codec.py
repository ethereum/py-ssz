from eth_utils import (
    is_bytes,
)

from ssz.sedes import (
    sedes_by_name,
)
from ssz.sedes.base import (
    BaseSedes,
)
from ssz.utils import (
    infer_sedes,
)


def encode(value, sedes=None):
    """
    Encode object in SSZ format.
    `sedes` needs to be explicitly mentioned for encode/decode
    of integers(as of now).
    `sedes` parameter could be given as a string or as the
    actual sedes object itself.
    """
    if sedes is not None:
        if sedes in sedes_by_name:
            # Get the actual sedes object from string representation
            sedes_obj = sedes_by_name[sedes]
        else:
            sedes_obj = sedes

        if not isinstance(sedes_obj, BaseSedes):
            raise TypeError("Invalid sedes object")

    else:
        sedes_obj = infer_sedes(value)

    serialized_obj = sedes_obj.serialize(value)
    return serialized_obj


def decode(ssz, sedes):
    """
    Decode a SSZ encoded object.
    """
    if not is_bytes(ssz):
        raise TypeError(f"Can only decode SSZ bytes, got type {type(ssz).__name__}")

    value = sedes.deserialize(ssz)
    return value
