import pytest

from ssz import (
    decode,
    encode,
)
from ssz.sedes import (
    Bitlist,
)


@pytest.mark.parametrize(
    'size, value, expected',
    (
        (16, tuple(), b'\x01'),
        (16, (0b1, 0b0,), b'\x05'),
        (16, (0b1,) + (0b0,) * 15, b'\x01\x00\x01'),
    ),
)
def test_bitlist_serialize_values(size, value, expected):
    Foo = Bitlist(size)
    assert encode(value, Foo) == expected
    assert Foo.serialize(bytearray(value)) == expected


@pytest.mark.parametrize(
    'size, value,expected',
    (
        (16, b'\x01', tuple()),
        (16, b'\x05', (True, False,)),
        (16, b'\x01\x00\x01', (True,) + (False,) * 15),
    ),
)
def test_bitlist_deserialize_values(size, value, expected):
    Foo = Bitlist(size)
    assert Foo.deserialize(value) == expected


@pytest.mark.parametrize(
    'size, value',
    (
        # (16, tuple()),
        (16, (True, False,)),
        (16, (True,) + (False,) * 15),
    ),
)
def test_bitlist_round_trip_no_sedes(size, value):
    Foo = Bitlist(size)
    assert decode(encode(value, Foo), Foo) == value
