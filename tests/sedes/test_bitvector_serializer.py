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
        (0, (), b''),
        (16, (0b1,) + (0b0,) * 15, b'\x01\x00'),
        (16, (0b0,) + (0b1,) + (0b0,) * 14, b'\x02\x00'),
        (16, (0b0,) * 15 + (0b1,), b'\x00\x80'),
        (16, (0b1,) * 16, b'\xff\xff'),
    ),
)
def test_bitvector_serialize_values(size, value, expected):
    foo = Bitvector(size)
    assert encode(value, foo) == expected
    assert foo.serialize(bytearray(value)) == expected


@pytest.mark.parametrize(
    'size, value,expected',
    (
        (0, b'', ()),
        (16, b'\x01\x00', (0b1,) + (0b0,) * 15),
        (16, b'\x02\x00', (0b0,) + (0b1,) + (0b0,) * 14),
        (16, b'\x00\x80', (0b0,) * 15 + (0b1,)),
        (16, b'\xff\xff', (0b1,) * 16),
    ),
)
def test_bitvector_deserialize_values(size, value, expected):
    foo = Bitvector(size)
    assert foo.deserialize(value) == expected


@pytest.mark.parametrize(
    'size, value',
    (
        (16, (0b1,) + (0b0,) * 15),
    ),
)
def test_bitvector_round_trip_no_sedes(size, value):
    foo = Bitvector(size)
    assert decode(encode(value, foo), foo) == value
