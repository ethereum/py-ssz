from ssz.exceptions import (
    SerializationError,
)
from ssz.sedes.base import (
    BasicSedes,
)


class UInt(BasicSedes[int, int]):

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
            return value.to_bytes(self.size, "little")
        except OverflowError:
            raise SerializationError(
                f"{value} is too large to be serialized in {self.size * 8} bits"
            )

    def deserialize_content(self, content: bytes) -> int:
        return int.from_bytes(content, "little")


uint8 = UInt(8)
uint16 = UInt(16)
uint32 = UInt(32)
uint64 = UInt(64)
uint128 = UInt(128)
uint256 = UInt(256)
