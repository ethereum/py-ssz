import pytest

from eth_utils import (
    decode_hex,
    encode_hex,
)

import ssz
from ssz.sedes import (
    Boolean,
    Byte,
    UInt,
    Vector,
    boolean,
    uint8,
)


@pytest.mark.parametrize(("value", "serialized"), ((True, "0x01"), (False, "0x00")))
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
        (256, 0xAA * sum(256**i for i in range(32)), "0x" + "aa" * 32),
        (256, 2**256 - 1, "0x" + "ff" * 32),
    ),
)
def test_uint(bit_length, value, serialized):
    uint = UInt(bit_length)
    assert encode_hex(ssz.encode(value, uint)) == serialized
    assert ssz.decode(decode_hex(serialized), uint) == value


@pytest.mark.parametrize(("sedes", "id"), ((UInt(64), "UInt64"), (boolean, "Boolean")))
def test_get_sedes_id(sedes, id):
    assert sedes.get_sedes_id() == id


@pytest.mark.parametrize(
    ("sedes1", "sedes2"), ((uint8, uint8), (UInt(8), UInt(8)), (UInt(256), UInt(256)))
)
def test_uint_eq(sedes1, sedes2):
    assert sedes1 == sedes1
    assert sedes2 == sedes2
    assert sedes1 == sedes2
    assert hash(sedes1) == hash(sedes2)


@pytest.mark.parametrize(
    ("sedes1", "sedes2"),
    (
        (UInt(8), UInt(256)),
        (UInt(8), Byte()),
        (UInt(8), boolean),
        (UInt(8), Vector(UInt(8), 1)),
    ),
)
def test_uint_neq(sedes1, sedes2):
    assert sedes1 != sedes2
    assert hash(sedes1) != hash(sedes2)


@pytest.mark.parametrize(
    ("sedes1", "sedes2"), ((boolean, boolean), (Boolean(), Boolean()))
)
def test_bool_eq(sedes1, sedes2):
    assert sedes1 == sedes1
    assert sedes2 == sedes2
    assert sedes1 == sedes2
    assert hash(sedes1) == hash(sedes2)


@pytest.mark.parametrize(
    ("sedes1", "sedes2"),
    ((boolean, uint8), (boolean, Byte()), (boolean, Vector(boolean, 1))),
)
def test_bool_neq(sedes1, sedes2):
    assert sedes1 != sedes2
    assert hash(sedes1) != hash(sedes2)
