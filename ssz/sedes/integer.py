from ssz.exceptions import (
    SerializationError,
)
from ssz.sedes.base import (
    FixedSizedSedes,
)


class UnsignedInteger(FixedSizedSedes[int, int]):

    def __init__(self, num_bits: int) -> None:
        if num_bits % 8 != 0:
            raise ValueError(
                "Number of bits must be a multiple of 8"
            )
        super().__init__(num_bits // 8)

    def serialize_content(self, value: int) -> bytes:
        if value < 0:
            raise SerializationError(
                f"Can only serialize non-negative integers, got {value}",
            )

        try:
            return value.to_bytes(self.length, 'big')
        except OverflowError:
            raise SerializationError(
                f"{value} is too large to be serialized in {self.length * 8} bits"
            )

    def deserialize_content(self, content: bytes) -> int:
        return int.from_bytes(content, 'big')


uint8 = UnsignedInteger(8)
uint16 = UnsignedInteger(16)
uint24 = UnsignedInteger(24)
uint32 = UnsignedInteger(32)
uint40 = UnsignedInteger(40)
uint48 = UnsignedInteger(48)
uint56 = UnsignedInteger(56)
uint64 = UnsignedInteger(64)
uint128 = UnsignedInteger(128)
uint256 = UnsignedInteger(256)
uint384 = UnsignedInteger(384)
uint512 = UnsignedInteger(512)
