from .boolean import (  # noqa: F401
    boolean,
    Boolean,
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
    UnsignedInteger,
)


sedes_by_name = {
    "boolean": boolean,
    "uint8": uint8,
    "uint16": uint16,
    "uint24": uint24,
    "uint32": uint32,
    "uint40": uint40,
    "uint48": uint48,
    "uint56": uint56,
    "uint64": uint64,
}
