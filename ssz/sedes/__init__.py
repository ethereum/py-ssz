from .boolean import (  # noqa: F401
    boolean,
    Boolean,
)

from .bytes import (  # noqa: F401
    bytes_sedes,
    Bytes,
)

from .bytes_n import (  # noqa: F401
    bytes32,
    bytes48,
    bytes96,
    BytesN,
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
    boolean_list,
    bytes_list,
    empty_list,
    uint32_list,
    bytes32_list,
    bytes48_list,
    bytes96_list,
    List,
)

from .base import (  # noqa: F401
    BaseSedes,
)

from .serializable import (  # noqa: F401
    Serializable,
)


sedes_by_name = {
    "boolean": boolean,
    "boolean_list": boolean_list,
    "bytes_list": bytes_list,
    "bytes_sedes": bytes_sedes,
    "bytes32": bytes32,
    "bytes48": bytes48,
    "bytes96": bytes96,
    "empty_list": empty_list,
    "uint32_list": uint32_list,
    "bytes32_list": bytes32_list,
    "bytes48_list": bytes48_list,
    "bytes96_list": bytes96_list,
    "uint8": uint8,
    "uint16": uint16,
    "uint24": uint24,
    "uint32": uint32,
    "uint40": uint40,
    "uint48": uint48,
    "uint56": uint56,
    "uint64": uint64,
}
