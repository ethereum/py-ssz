from eth_utils import (
    is_bytes,
)

from ssz.exceptions import (
    DecodingError,
)
from ssz.utils import (
    infer_sedes,
)


def encode(obj):
    """
    Encode object in SSZ format.
    """
    serialized_obj = infer_sedes(obj).serialize(obj)
    return serialized_obj


def decode(ssz, sedes):
    """
    Decode a SSZ encoded object.
    """
    if not is_bytes(ssz):
        raise DecodingError('Can only decode SSZ bytes, got type %s' % type(ssz).__name__, ssz)

    obj = sedes.deserialize(ssz)
    return obj
