import collections
from collections.abc import (
    Iterable,
    Sequence,
)

from ssz.sedes.base import (
    BaseSedes,
)
from ssz.sedes.boolean import (
    boolean,
)
from ssz.sedes.byte_list import (
    byte_list,
)
from ssz.sedes.list import (
    List,
    empty_list,
)


def infer_list_sedes(value):
    if len(value) == 0:
        return empty_list
    else:
        try:
            element_sedes = infer_sedes(value[0])
        except TypeError:
            raise TypeError("Could not infer sedes for list elements")
        else:
            return List(element_sedes)


def infer_sedes(value):
    """
    Try to find a sedes objects suitable for a given Python object.
    """
    if isinstance(value.__class__, BaseSedes):
        # Mainly used for `Serializable` Classes
        return value.__class__

    elif isinstance(value, bool):
        return boolean

    elif isinstance(value, int):
        raise TypeError("uint sedes object or uint string needs to be specified for ints")

    elif isinstance(value, (bytes, bytearray)):
        return byte_list

    elif isinstance(value, Sequence):
        return infer_list_sedes(value)

    elif isinstance(value, Iterable):
        raise TypeError("Cannot infer list sedes for iterables that are not sequences")

    else:
        raise TypeError(f"Did not find sedes handling type {type(value).__name__}")


def get_duplicates(values):
    counts = collections.Counter(values)
    return tuple(
        item
        for item, num in counts.items()
        if num > 1
    )
