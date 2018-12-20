from collections.abc import (
    Iterable,
)

from eth_utils.toolz import (
    peek,
)

from ssz.sedes import (
    List,
    boolean,
    bytes_sedes,
    empty_list,
)


def is_sedes(obj):
    """
    Check if `obj` is a sedes object.
    A sedes object is characterized by having the methods
    `serialize(obj)` and `deserialize(serial)`.
    """
    return hasattr(obj, 'serialize') and hasattr(obj, 'deserialize')


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
            raise TypeError(
                "Could not infer sedes for list elements",
                obj
            )
        else:
            return List(element_sedes)


def infer_sedes(obj):
    """
    Try to find a sedes objects suitable for a given Python object.
    """
    if is_sedes(obj.__class__):
        # Return sedes directly, if such a sedes exists with the class name
        # Mainly used for `Serializable` Classes
        return obj.__class__

    if isinstance(obj, bool):
        return boolean

    elif isinstance(obj, int):
        raise TypeError(
            'uint sedes object or uint string needs to be specified for ints',
            obj
        )

    elif isinstance(obj, (bytes, bytearray)):
        return bytes_sedes

    elif isinstance(obj, Iterable):
        return infer_list_sedes(obj)

    msg = 'Did not find sedes handling type {}'.format(type(obj).__name__)
    raise TypeError(msg)
