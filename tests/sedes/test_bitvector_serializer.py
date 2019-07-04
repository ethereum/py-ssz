import pytest

from ssz import (
    decode,
    encode,
)
from ssz.sedes import (
    Bitvector,
)


@pytest.mark.parametrize(
    'size, value, expected',
    (
        (16, (0b1,) + (0b0,) * 15, b'\x01\x00'),
        (16, (0b0,) + (0b1,) + (0b0,) * 14, b'\x02\x00'),
        (16, (0b0,) * 15 + (0b1,), b'\x00\x80'),
        (16, (0b1,) * 16, b'\xff\xff'),
    ),
)
def test_bytes_serialize_values(size, value, expected):
    Foo = Bitvector(size)
    assert encode(value, Foo) == expected
    assert Foo.serialize(bytearray(value)) == expected


@pytest.mark.parametrize(
    'size, value,expected',
    (
        (16, b'\x01\x00', (0b1,) + (0b0,) * 15),
        (16, b'\x02\x00', (0b0,) + (0b1,) + (0b0,) * 14),
        (16, b'\x00\x80', (0b0,) * 15 + (0b1,)),
        (16, b'\xff\xff', (0b1,) * 16),
    ),
)
def test_bytes_deserialize_values(size, value, expected):
    Foo = Bitvector(size)
    assert Foo.deserialize(value) == expected


@pytest.mark.parametrize(
    'size, value',
    (
        (16, (0b1,) + (0b0,) * 15),
    ),
)
def test_bytes_round_trip_no_sedes(size, value):
    Foo = Bitvector(size)
    assert decode(encode(value, Foo), Foo) == value
