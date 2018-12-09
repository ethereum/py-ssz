from .boolean import (  # noqa: F401
    boolean,
    Boolean,
)

from .hash import (  # noqa: F401
    address,
    hash32,
    Hash,
)

from .integer import (  # noqa: F401
    uint8,
    uint16,
    uint24,
    uint32,
    uint40,
    uint48,
    uint56,
    uint64,
    uint128,
    uint256,
    uint384,
    uint512,
    UnsignedInteger,
)


sedes_by_name = {
    "address": address,
    "boolean": boolean,
    "hash32": hash32,
    "uint8": uint8,
    "uint16": uint16,
    "uint24": uint24,
    "uint32": uint32,
    "uint40": uint40,
    "uint48": uint48,
    "uint56": uint56,
    "uint64": uint64,
}
