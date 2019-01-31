from ssz.exceptions import (
    SerializationError,
)
from ssz.sedes.base import (
    FixedSizedSedes,
)


class UInt(FixedSizedSedes[int, int]):

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


uint8 = UInt(8)
uint16 = UInt(16)
uint24 = UInt(24)
uint32 = UInt(32)
uint40 = UInt(40)
uint48 = UInt(48)
uint56 = UInt(56)
uint64 = UInt(64)

uint72 = UInt(72)
uint80 = UInt(80)
uint88 = UInt(88)
uint96 = UInt(96)
uint104 = UInt(104)
uint112 = UInt(112)
uint120 = UInt(120)
uint128 = UInt(128)

uint136 = UInt(136)
uint144 = UInt(144)
uint152 = UInt(152)
uint160 = UInt(160)
uint168 = UInt(168)
uint176 = UInt(176)
uint184 = UInt(184)
uint192 = UInt(192)

uint200 = UInt(200)
uint208 = UInt(208)
uint216 = UInt(216)
uint224 = UInt(224)
uint232 = UInt(232)
uint240 = UInt(240)
uint248 = UInt(248)
uint256 = UInt(256)

uint264 = UInt(264)
uint272 = UInt(272)
uint280 = UInt(280)
uint288 = UInt(288)
uint296 = UInt(296)
uint304 = UInt(304)
uint312 = UInt(312)
uint320 = UInt(320)

uint328 = UInt(328)
uint336 = UInt(336)
uint344 = UInt(344)
uint352 = UInt(352)
uint360 = UInt(360)
uint368 = UInt(368)
uint376 = UInt(376)
uint384 = UInt(384)

uint392 = UInt(392)
uint400 = UInt(400)
uint408 = UInt(408)
uint416 = UInt(416)
uint424 = UInt(424)
uint432 = UInt(432)
uint440 = UInt(440)
uint448 = UInt(448)

uint456 = UInt(456)
uint464 = UInt(464)
uint472 = UInt(472)
uint480 = UInt(480)
uint488 = UInt(488)
uint496 = UInt(496)
uint504 = UInt(504)
uint512 = UInt(512)
