import collections
from collections.abc import (
    Iterable,
)

from eth_utils.toolz import (
    peek,
)

from ssz.sedes import (
    BaseSedes,
    List,
    boolean,
    bytes_sedes,
    empty_list,
)


def infer_list_sedes(obj):
    try:
        first_element, iterator = peek(obj)
    except StopIteration:
        # For empty lists we use any empty_list sedes.
        return empty_list
    else:
        try:
            element_sedes = infer_sedes(first_element)
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
        return bytes_sedes

    elif isinstance(obj, Iterable):
        return infer_list_sedes(obj)

    else:
        raise TypeError(f"Did not find sedes handling type {type(value).__name__}")


def get_duplicates(values):
    counts = collections.Counter(values)
    return tuple(
        item
        for item, num in counts.items()
        if num > 1
    )
