from .boolean import (  # noqa: F401
    boolean,
    Boolean,
)

from .bytes import (  # noqa: F401
    bytes_sedes,
    Bytes,
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
    address_list,
    boolean_list,
    empty_list,
    hash32_list,
    uint32_list,
    List,
)


sedes_by_name = {
    "address_list": address_list,
    "address": address,
    "boolean": boolean,
    "boolean_list": boolean_list,
    "bytes_sedes": bytes_sedes,
    "empty_list": empty_list,
    "hash32": hash32,
    "hash32_list": hash32_list,
    "uint32_list": uint32_list,
    "uint8": uint8,
    "uint16": uint16,
    "uint24": uint24,
    "uint32": uint32,
    "uint40": uint40,
    "uint48": uint48,
    "uint56": uint56,
    "uint64": uint64,
}
