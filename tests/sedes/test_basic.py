from eth_utils import (
    decode_hex,
    encode_hex,
)
import pytest

import ssz
from ssz.sedes import (
    UInt,
    boolean,
)


@pytest.mark.parametrize(
    ("value", "serialized"),
    (
        (True, "0x01"),
        (False, "0x00"),
    ),
)
def test_boolean(value, serialized):
    assert encode_hex(ssz.encode(value, boolean)) == serialized
    assert ssz.decode(decode_hex(serialized), boolean) == value


@pytest.mark.parametrize(
    ("bit_length", "value", "serialized"),
    (
        (8, 0, "0x00"),
        (8, 16, "0x10"),
        (8, 255, "0xff"),

        (16, 0, "0x0000"),
        (16, 256, "0x0001"),
        (16, 65536 - 1, "0xffff"),

        (32, sum((i + 1) * 256**i for i in range(4)), "0x01020304"),

        (256, 0, "0x" + "00" * 32),
        (256, 0xaa * sum(256**i for i in range(32)), "0x" + "aa" * 32),
        (256, 2**256 - 1, "0x" + "ff" * 32),
    ),
)
def test_uint(bit_length, value, serialized):
    uint = UInt(bit_length)
    assert encode_hex(ssz.encode(value, uint)) == serialized
    assert ssz.decode(decode_hex(serialized), uint) == value
