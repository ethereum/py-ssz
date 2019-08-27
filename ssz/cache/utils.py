import functools
from typing import (
    Any,
)

from ssz.sedes.base import (
    TSedes,
)


def get_key(sedes: TSedes, value: Any) -> str:
    key = _get_key(sedes, value).hex()
    sedes_name = type(sedes).__name__
    if len(key) > 0:
        return sedes_name + key
    else:
        # If the serialized result is empty, use sedes name as the key
        return sedes_name


@functools.lru_cache(maxsize=2**12)
def _get_key(sedes: TSedes, value: Any) -> bytes:
    return sedes.serialize(value)
