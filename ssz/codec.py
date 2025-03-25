from typing import (
    Optional,
    Union,
)

from eth_utils import (
    is_bytes,
)

from ssz.sedes import (
    infer_sedes,
    sedes_by_name,
)
from ssz.sedes.base import (
    BaseSedes,
)
from ssz.typing import (
    TDeserialized,
    TSerializable,
)


def encode(
    value: TSerializable,
    sedes: Optional[Union[BaseSedes[TSerializable, TDeserialized], str]] = None,
) -> bytes:
    """
    Encode object in SSZ format.

    Args
    ----
        value: TSerializable: Object to encode in SSZ format.

        sedes: BaseSedes: Optional sedes object or string to use for encoding.
        If not given, the default sedes object for the given object is used.

    Returns
    -------
        bytes: Encoded object in SSZ format.

    Raises
    ------
        TypeError: If the given sedes object is not a subclass of BaseSedes.

    Note: The sedes argument is required for int objects at this time.

    """
    if sedes is None:
        sedes = infer_sedes(value)

    if isinstance(sedes, str):
        if sedes not in sedes_by_name:
            raise TypeError(f"Unknown sedes name: {sedes}")
        sedes = sedes_by_name[sedes]

    if not isinstance(sedes, BaseSedes):
        raise TypeError("Invalid sedes object")

    return sedes.serialize(value)


def decode(ssz: bytes, sedes: BaseSedes[TSerializable, TDeserialized]) -> TDeserialized:
    """
    Decode a SSZ encoded object.

    Args
    ----
        ssz: bytes: SSZ encoded object to decode.

        sedes: BaseSedes: sedes object to use for decoding.

    Returns
    -------
        TDeserialized: Decoded object.

    Raises
    ------
        TypeError: If the ssz object is not bytes or the given sedes object is not a
        subclass of BaseSedes

    """
    if not is_bytes(ssz):
        raise TypeError(f"Can only decode SSZ bytes, got type {type(ssz).__name__}")

    if not isinstance(sedes, BaseSedes):
        raise TypeError("Invalid sedes object")

    value = sedes.deserialize(ssz)
    return value
