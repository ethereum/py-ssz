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
            return value.to_bytes(self.length, "little")
        except OverflowError:
            raise SerializationError(
                f"{value} is too large to be serialized in {self.length * 8} bits"
            )

    def deserialize_content(self, content: bytes) -> int:
        return int.from_bytes(content, "little")


uint8 = UnsignedInteger(8)
uint16 = UnsignedInteger(16)
uint24 = UnsignedInteger(24)
uint32 = UnsignedInteger(32)
uint40 = UnsignedInteger(40)
uint48 = UnsignedInteger(48)
uint56 = UnsignedInteger(56)
uint64 = UnsignedInteger(64)

uint72 = UnsignedInteger(72)
uint80 = UnsignedInteger(80)
uint88 = UnsignedInteger(88)
uint96 = UnsignedInteger(96)
uint104 = UnsignedInteger(104)
uint112 = UnsignedInteger(112)
uint120 = UnsignedInteger(120)
uint128 = UnsignedInteger(128)

uint136 = UnsignedInteger(136)
uint144 = UnsignedInteger(144)
uint152 = UnsignedInteger(152)
uint160 = UnsignedInteger(160)
uint168 = UnsignedInteger(168)
uint176 = UnsignedInteger(176)
uint184 = UnsignedInteger(184)
uint192 = UnsignedInteger(192)

uint200 = UnsignedInteger(200)
uint208 = UnsignedInteger(208)
uint216 = UnsignedInteger(216)
uint224 = UnsignedInteger(224)
uint232 = UnsignedInteger(232)
uint240 = UnsignedInteger(240)
uint248 = UnsignedInteger(248)
uint256 = UnsignedInteger(256)

uint264 = UnsignedInteger(264)
uint272 = UnsignedInteger(272)
uint280 = UnsignedInteger(280)
uint288 = UnsignedInteger(288)
uint296 = UnsignedInteger(296)
uint304 = UnsignedInteger(304)
uint312 = UnsignedInteger(312)
uint320 = UnsignedInteger(320)

uint328 = UnsignedInteger(328)
uint336 = UnsignedInteger(336)
uint344 = UnsignedInteger(344)
uint352 = UnsignedInteger(352)
uint360 = UnsignedInteger(360)
uint368 = UnsignedInteger(368)
uint376 = UnsignedInteger(376)
uint384 = UnsignedInteger(384)

uint392 = UnsignedInteger(392)
uint400 = UnsignedInteger(400)
uint408 = UnsignedInteger(408)
uint416 = UnsignedInteger(416)
uint424 = UnsignedInteger(424)
uint432 = UnsignedInteger(432)
uint440 = UnsignedInteger(440)
uint448 = UnsignedInteger(448)

uint456 = UnsignedInteger(456)
uint464 = UnsignedInteger(464)
uint472 = UnsignedInteger(472)
uint480 = UnsignedInteger(480)
uint488 = UnsignedInteger(488)
uint496 = UnsignedInteger(496)
uint504 = UnsignedInteger(504)
uint512 = UnsignedInteger(512)
