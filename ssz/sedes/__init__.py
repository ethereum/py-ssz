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
    UnsignedInteger,

    uint8,
    uint16,
    uint24,
    uint32,
    uint40,
    uint48,
    uint56,
    uint64,

    uint72,
    uint80,
    uint88,
    uint96,
    uint104,
    uint112,
    uint120,
    uint128,

    uint136,
    uint144,
    uint152,
    uint160,
    uint168,
    uint176,
    uint184,
    uint192,

    uint200,
    uint208,
    uint216,
    uint224,
    uint232,
    uint240,
    uint248,
    uint256,

    uint264,
    uint272,
    uint280,
    uint288,
    uint296,
    uint304,
    uint312,
    uint320,

    uint328,
    uint336,
    uint344,
    uint352,
    uint360,
    uint368,
    uint376,
    uint384,

    uint392,
    uint400,
    uint408,
    uint416,
    uint424,
    uint432,
    uint440,
    uint448,

    uint456,
    uint464,
    uint472,
    uint480,
    uint488,
    uint496,
    uint504,
    uint512,
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
    FixedSizedSedes,
    LengthPrefixedSedes,
)

from .container import (
    Container,
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

    "uint72": uint72,
    "uint80": uint80,
    "uint88": uint88,
    "uint96": uint96,
    "uint104": uint104,
    "uint112": uint112,
    "uint120": uint120,
    "uint128": uint128,

    "uint136": uint136,
    "uint144": uint144,
    "uint152": uint152,
    "uint160": uint160,
    "uint168": uint168,
    "uint176": uint176,
    "uint184": uint184,
    "uint192": uint192,

    "uint200": uint200,
    "uint208": uint208,
    "uint216": uint216,
    "uint224": uint224,
    "uint232": uint232,
    "uint240": uint240,
    "uint248": uint248,
    "uint256": uint256,

    "uint264": uint264,
    "uint272": uint272,
    "uint280": uint280,
    "uint288": uint288,
    "uint296": uint296,
    "uint304": uint304,
    "uint312": uint312,
    "uint320": uint320,

    "uint328": uint328,
    "uint336": uint336,
    "uint344": uint344,
    "uint352": uint352,
    "uint360": uint360,
    "uint368": uint368,
    "uint376": uint376,
    "uint384": uint384,

    "uint392": uint392,
    "uint400": uint400,
    "uint408": uint408,
    "uint416": uint416,
    "uint424": uint424,
    "uint432": uint432,
    "uint440": uint440,
    "uint448": uint448,

    "uint456": uint456,
    "uint464": uint464,
    "uint472": uint472,
    "uint480": uint480,
    "uint488": uint488,
    "uint496": uint496,
    "uint504": uint504,
    "uint512": uint512,
}
