from collections.abc import (
    Iterable,
)
from typing import (
    Any,
    Union,
    cast,
)

from ssz.hashable_structure import (
    BaseHashableStructure,
)
from ssz.typing import (
    TDeserialized,
    TSerializable,
)

from .base import (
    BaseProperCompositeSedes,
    BaseSedes,
)
from .basic import (
    BasicSedes,
    ProperCompositeSedes,
)
from .bitlist import (
    Bitlist,
)
from .bitvector import (
    Bitvector,
)
from .boolean import (
    Boolean,
    boolean,
)
from .byte import (
    Byte,
    byte,
)
from .byte_list import (
    ByteList,
)
from .byte_vector import (
    ByteVector,
    bytes1,
    bytes4,
    bytes32,
    bytes48,
    bytes96,
)
from .container import (
    Container,
)
from .list import (
    List,
)
from .serializable import (
    Serializable,
)
from .signed_serializable import (
    SignedSerializable,
)
from .uint import (
    UInt,
    uint8,
    uint16,
    uint32,
    uint64,
    uint128,
    uint256,
)
from .vector import (
    Vector,
)

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


def infer_sedes(
    value: Any,
) -> Union[
    BaseSedes[TSerializable, TDeserialized],
    BaseProperCompositeSedes[TSerializable, TDeserialized],
]:
    """
    Try to find a sedes objects suitable for a given Python object.
    """
    if isinstance(value.__class__, BaseSedes):
        return value.__class__
    elif isinstance(value, BaseHashableStructure):
        return value.sedes
    elif isinstance(value, bool):
        return cast(BaseSedes[bool, bool], boolean)
    elif isinstance(value, int):
        raise TypeError(
            "uint sedes object or uint string needs to be specified for ints"
        )
    elif isinstance(value, Iterable):
        raise TypeError("Cannot infer list sedes for iterables that are not sequences")
    else:
        raise TypeError(f"Did not find sedes handling type {type(value).__name__}")
