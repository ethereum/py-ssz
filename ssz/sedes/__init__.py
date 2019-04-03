from collections.abc import (
    Iterable,
    Sequence,
)

from .base import (  # noqa: F401
    BaseSedes,
    BasicSedes,
    CompositeSedes,
)
from .boolean import (  # noqa: F401
    Boolean,
    boolean,
)
from .byte import (  # noqa: F401
    Byte,
    byte,
)
from .byte_list import (  # noqa: F401
    ByteList,
    byte_list,
)
from .byte_vector import (  # noqa: F401
    ByteVector,
    bytes4,
    bytes32,
    bytes48,
    bytes96,
)
from .container import (  # noqa: F401
    Container,
)
from .list import (  # noqa: F401
    List,
    empty_list,
)
from .serializable import (  # noqa: F401
    Serializable,
)
from .uint import (  # noqa: F401
    UInt,
    uint8,
    uint16,
    uint32,
    uint64,
    uint128,
    uint256,
)
from .vector import (  # noqa: F401
    Vector,
)

sedes_by_name = {
    "bool": boolean,

    "byte": byte,
    "bytes4": bytes4,
    "bytes32": bytes32,
    "bytes48": bytes48,
    "bytes96": bytes96,
    "byte_list": byte_list,
    "empty_list": empty_list,

    "uint8": uint8,
    "uint16": uint16,
    "uint32": uint32,
    "uint64": uint64,
    "uint128": uint128,
    "uint256": uint256,
}


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
        return value.__class__  # Mainly used for `Serializable` classes
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
