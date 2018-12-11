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

from .list import (  # noqa: F401
    addr_list,
    bool_list,
    hash_list,
    int_list,
)


sedes_by_name = {
    "addr_list": addr_list,
    "address": address,
    "boolean": boolean,
    "bool_list": bool_list,
    "hash32": hash32,
    "hash_list": hash_list,
    "int_list": int_list,
    "uint8": uint8,
    "uint16": uint16,
    "uint24": uint24,
    "uint32": uint32,
    "uint40": uint40,
    "uint48": uint48,
    "uint56": uint56,
    "uint64": uint64,
}
