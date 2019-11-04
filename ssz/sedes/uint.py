from typing import Any

from ssz.exceptions import DeserializationError, SerializationError
from ssz.sedes.basic import BasicSedes


class UInt(BasicSedes[int, int]):
    def __init__(self, num_bits: int) -> None:
        if num_bits % 8 != 0:
            raise ValueError("Number of bits must be a multiple of 8")
        self.num_bits = num_bits
        super().__init__(num_bits // 8)

    def serialize(self, value: int) -> bytes:
        if value < 0:
            raise SerializationError(
                f"Can only serialize non-negative integers, got {value}"
            )

        try:
            return value.to_bytes(self.size, "little")
        except OverflowError:
            raise SerializationError(
                f"{value} is too large to be serialized in {self.size * 8} bits"
            )

    def deserialize(self, data: bytes) -> int:
        if len(data) != self.size:
            raise DeserializationError(
                f"Cannot deserialize length {len(data)} byte-string as uint{self.size*8}"
            )
        return int.from_bytes(data, "little")

    def get_sedes_id(self) -> str:
        return f"{self.__class__.__name__}{self.num_bits}"

    def __hash__(self) -> int:
        return hash((hash(UInt), self.num_bits))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, UInt) and other.num_bits == self.num_bits


uint8 = UInt(8)
uint16 = UInt(16)
uint32 = UInt(32)
uint64 = UInt(64)
uint128 = UInt(128)
uint256 = UInt(256)
