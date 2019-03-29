from eth_utils import (
    is_bytes,
)

from ssz.sedes import (
    Serializable,
    infer_sedes,
    sedes_by_name,
)
from ssz.sedes.base import (
    BaseSedes,
)


def encode(value, sedes=None, cache=True):
    """
    Encode object in SSZ format.
    `sedes` needs to be explicitly mentioned for encode/decode
    of integers(as of now).
    `sedes` parameter could be given as a string or as the
    actual sedes object itself.

    If `value` has an attribute :attr:`_cached_ssz` (as, notably,
    :class:`ssz.sedes.Serializable`) and its value is not `None`, this value is
    returned bypassing serialization and encoding, unless `sedes` is given (as
    the cache is assumed to refer to the standard serialization which can be
    replaced by specifying `sedes`).
    If `value` is a :class:`ssz.sedes.Serializable` and `cache` is true, the result of
    the encoding will be stored in :attr:`_cached_ssz` if it is empty.
    """
    if isinstance(value, Serializable):
        cached_ssz = value._cached_ssz
        if sedes is None and cached_ssz is not None:
            return cached_ssz
        else:
            really_cache = cache and sedes is None
    else:
        really_cache = False

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

    if really_cache:
        value._cached_ssz = serialized_obj

    return serialized_obj


def decode(ssz, sedes):
    """
    Decode a SSZ encoded object.
    """
    if not is_bytes(ssz):
        raise TypeError(f"Can only decode SSZ bytes, got type {type(ssz).__name__}")

    value = sedes.deserialize(ssz)
    return value
