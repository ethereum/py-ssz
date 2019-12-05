from collections.abc import Iterable

from ssz.abc import HashableStructureAPI

from .base import BaseSedes  # noqa: F401
from .basic import BasicSedes, ProperCompositeSedes  # noqa: F401
from .bitlist import Bitlist  # noqa: F401
from .bitvector import Bitvector  # noqa: F401
from .boolean import Boolean, boolean  # noqa: F401
from .byte import Byte, byte  # noqa: F401
from .byte_vector import (  # noqa: F401
    ByteVector,
    bytes1,
    bytes4,
    bytes32,
    bytes48,
    bytes96,
)
from .container import Container  # noqa: F401
from .list import List  # noqa: F401
from .serializable import Serializable  # noqa: F401
from .signed_serializable import SignedSerializable  # noqa: F401
from .uint import UInt, uint8, uint16, uint32, uint64, uint128, uint256  # noqa: F401
from .vector import Vector  # noqa: F401

sedes_by_name = {
    "bool": boolean,
    "byte": byte,
    "bytes4": bytes4,
    "bytes32": bytes32,
    "bytes48": bytes48,
    "bytes96": bytes96,
    "uint8": uint8,
    "uint16": uint16,
    "uint32": uint32,
    "uint64": uint64,
    "uint128": uint128,
    "uint256": uint256,
}


def infer_sedes(value):
    """
    Try to find a sedes objects suitable for a given Python object.
    """
    if isinstance(value.__class__, BaseSedes):
        return value.__class__
    elif isinstance(value, HashableStructureAPI):
        return value.sedes
    elif isinstance(value, bool):
        return boolean
    elif isinstance(value, int):
        raise TypeError(
            "uint sedes object or uint string needs to be specified for ints"
        )
    elif isinstance(value, Iterable):
        raise TypeError("Cannot infer list sedes for iterables that are not sequences")
    else:
        raise TypeError(f"Did not find sedes handling type {type(value).__name__}")
