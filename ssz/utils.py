from collections.abc import (
    Iterable,
)

from toolz import (
    peek,
)

from ssz.sedes import (
    List,
    boolean,
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
        # For empty lists we can use any element sedes
        pass
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
    if isinstance(obj, bool):
        return boolean
    elif isinstance(obj, int):
        raise TypeError(
            'uint sedes object or uint string needs to be specified for ints',
            obj
        )
    elif isinstance(obj, Iterable):
        return infer_list_sedes(obj)

    msg = 'Did not find sedes handling type {}'.format(type(obj).__name__)
    raise TypeError(msg)
