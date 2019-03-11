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

from .uint import (  # noqa: F401
    UInt,
    uint8,
    uint16,
    uint32,
    uint64,
    uint128,
    uint256,
    uint512,
)

from .list import (  # noqa: F401
    empty_list,
    List,
)

from .base import (  # noqa: F401
    BaseSedes,
    FixedSizedSedes,
    LengthPrefixedSedes,
)

from .container import (  # noqa: F401
    Container,
)

from .serializable import (  # noqa: F401
    Serializable,
)


sedes_by_name = {
    "boolean": boolean,
    "bytes_sedes": bytes_sedes,
    "bytes32": bytes32,
    "bytes48": bytes48,
    "bytes96": bytes96,
    "empty_list": empty_list,

    "uint8": uint8,
    "uint16": uint16,
    "uint32": uint32,
    "uint64": uint64,
    "uint128": uint128,
    "uint256": uint256,
    "uint512": uint512,
}
