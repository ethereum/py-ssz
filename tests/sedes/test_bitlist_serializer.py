import pytest

from ssz import decode, encode
from ssz.sedes import Bitlist, Bitvector, List, boolean


@pytest.mark.parametrize(
    "size, value, expected",
    (
        (16, (), b"\x01"),
        (16, (True, False), b"\x05"),
        (16, (True,) + (False,) * 15, b"\x01\x00\x01"),
    ),
)
def test_bitlist_serialize_values(size, value, expected):
    foo = Bitlist(size)
    assert encode(value, foo) == expected
    assert foo.serialize(bytearray(value)) == expected


@pytest.mark.parametrize(
    "size, value,expected",
    (
        (16, b"\x01", tuple()),
        (16, b"\x05", (True, False)),
        (16, b"\x01\x00\x01", (True,) + (False,) * 15),
    ),
)
def test_bitlist_deserialize_values(size, value, expected):
    foo = Bitlist(size)
    assert foo.deserialize(value) == expected


@pytest.mark.parametrize(
    "size, value",
    (
        # (16, tuple()),
        (16, (True, False)),
        (16, (True,) + (False,) * 15),
    ),
)
def test_bitlist_round_trip_no_sedes(size, value):
    foo = Bitlist(size)
    assert decode(encode(value, foo), foo) == value


@pytest.mark.parametrize(("sedes", "id"), ((Bitlist(64), "Bitlist64"),))
def test_get_sedes_id(sedes, id):
    assert sedes.get_sedes_id() == id


@pytest.mark.parametrize(("sedes1", "sedes2"), ((Bitlist(2), Bitlist(2)),))
def test_eq(sedes1, sedes2):
    assert sedes1 == sedes1
    assert sedes2 == sedes2
    assert sedes1 == sedes2
    assert hash(sedes1) == hash(sedes2)


@pytest.mark.parametrize(
    ("sedes1", "sedes2"),
    (
        (Bitlist(2), Bitlist(3)),
        (Bitlist(2), Bitvector(2)),
        (Bitlist(2), List(boolean, 2)),
    ),
)
def test_neq(sedes1, sedes2):
    assert sedes1 != sedes2
    assert hash(sedes1) != hash(sedes2)
