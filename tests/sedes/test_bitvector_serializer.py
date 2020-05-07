import pytest

from ssz import decode, encode
from ssz.sedes import Bitlist, Bitvector, Vector, boolean


@pytest.mark.parametrize(
    "size, value, expected",
    (
        (16, (True,) + (False,) * 15, b"\x01\x00"),
        (16, (False,) + (True,) + (False,) * 14, b"\x02\x00"),
        (16, (False,) * 15 + (True,), b"\x00\x80"),
        (16, (True,) * 16, b"\xff\xff"),
    ),
)
def test_bitvector_serialize_values(size, value, expected):
    foo = Bitvector(size)
    assert encode(value, foo) == expected
    assert foo.serialize(bytearray(value)) == expected


@pytest.mark.parametrize(
    "size, value,expected",
    (
        (16, b"\x01\x00", (True,) + (False,) * 15),
        (16, b"\x02\x00", (False,) + (True,) + (False,) * 14),
        (16, b"\x00\x80", (False,) * 15 + (True,)),
        (16, b"\xff\xff", (True,) * 16),
    ),
)
def test_bitvector_deserialize_values(size, value, expected):
    foo = Bitvector(size)
    assert foo.deserialize(value) == expected


@pytest.mark.parametrize("size, value", ((16, (True,) + (False,) * 15),))
def test_bitvector_round_trip_no_sedes(size, value):
    foo = Bitvector(size)
    assert decode(encode(value, foo), foo) == value

    @pytest.mark.parametrize(("sedes", "id"), ((Bitvector(64), "Bitvector64"),))
    def test_get_sedes_id(sedes, id):
        assert sedes.get_sedes_id() == id


@pytest.mark.parametrize(("sedes1", "sedes2"), ((Bitvector(2), Bitvector(2)),))
def test_eq(sedes1, sedes2):
    assert sedes1 == sedes1
    assert sedes2 == sedes2
    assert sedes1 == sedes2
    assert hash(sedes1) == hash(sedes2)


@pytest.mark.parametrize(
    ("sedes1", "sedes2"),
    (
        (Bitvector(2), Bitvector(3)),
        (Bitvector(2), Bitlist(2)),
        (Bitvector(2), Vector(boolean, 2)),
    ),
)
def test_neq(sedes1, sedes2):
    assert sedes1 != sedes2
    assert hash(sedes1) != hash(sedes2)
