import itertools

from eth_utils import (
    decode_hex,
    encode_hex,
)
import pytest

import ssz
from ssz.exceptions import (
    DeserializationError,
)
from ssz.sedes import (
    Container,
    List,
    Vector,
    uint8,
)


@pytest.mark.parametrize(
    ("value", "serialized"),
    (
        ((), "0x"),
        ((0xaa,), "0xaa"),
        ((0xaa, 0xbb, 0xcc), "0xaabbcc"),
        ((0xaa,) * 256, "0x" + "aa" * 256),
        ((0xaa,) * (256**2 - 1), "0x" + "aa" * (256**2 - 1)),
    ),
)
def test_list(value, serialized):
    sedes = List(uint8, 2**32)
    assert encode_hex(ssz.encode(value, sedes)) == serialized
    assert ssz.decode(decode_hex(serialized), sedes) == value


def test_invalid_serialized_list():
    # ensure that an improperly read offset (not enough bytes) does not
    # incorrectly register as an empty list due to mis-interpreting the failed
    # stream read as the stream having been empty.
    data = decode_hex("0x0001")
    sedes = List(List(uint8, 2**32), 2**32)
    with pytest.raises(DeserializationError):
        ssz.decode(data, sedes=sedes)


@pytest.mark.parametrize(
    ("value", "serialized"),
    (
        ((), "0x"),
        ((0xaa,), "0xaa"),
        ((0xaa, 0xbb, 0xcc), "0xaabbcc"),
    ),
)
def test_tuple_of_static_sized_entries(value, serialized):
    sedes = Vector(uint8, len(value))
    assert encode_hex(ssz.encode(value, sedes)) == serialized
    assert ssz.decode(decode_hex(serialized), sedes) == value


@pytest.mark.parametrize(
    ("value", "serialized"),
    (
        (((),), "0x" "04000000"),
        (((0xaa,),), "0x" "04000000" "aa"),
        (((0xaa, 0xbb, 0xcc),), "0x" "04000000" "aabbcc"),
        (((), (), ()), "0x" "0c000000" "0c000000" "0c000000" ""),
        (
            ((0xaa,), (0xbb, 0xcc), (0xdd, 0xee, 0xff)),
            "0x" "0c000000" "0d000000" "0f000000" "aa" "bbcc" "ddeeff",
        ),
    )
)
def test_list_of_dynamic_sized_entries(value, serialized):
    sedes = Vector(List(uint8, 2**32), len(value))
    assert encode_hex(ssz.encode(value, sedes)) == serialized
    assert ssz.decode(decode_hex(serialized), sedes) == value


@pytest.mark.parametrize(
    ("value", "serialized"),
    (
        ((0xaa,), "0xaa"),
        ((0xaa, 0xbb, 0xcc), "0xaabbcc"),
    ),
)
def test_container_of_static_sized_fields(value, serialized):
    sedes = Container(tuple(itertools.repeat(uint8, len(value))))

    assert encode_hex(ssz.encode(value, sedes)) == serialized
    assert ssz.decode(decode_hex(serialized), sedes) == value


@pytest.mark.parametrize(
    ("fields", "value", "serialized"),
    (
        ((List(uint8, 2**32),), ((),), "0x" "04000000"),
        ((List(uint8, 2**32),), ((0xaa, 0xbb),), "0x" "04000000" "aabb"),
        ((uint8, List(uint8, 2**32),), (0xaa, (0xbb, 0xcc)), "0x" "aa" "05000000" "bbcc"),
        ((List(uint8, 2**32), uint8), ((0xaa, 0xbb), 0xcc), "0x" "05000000" "cc" "aabb"),
        (
            (List(uint8, 2**32), List(uint8, 2**32)),
            ((0xaa, 0xbb), (0xcc, 0xdd)),
            "0x" "08000000" "0a000000" "aabbccdd",
        )
    )
)
def test_container_of_dynamic_sized_fields(fields, value, serialized):
    sedes = Container(fields)

    assert encode_hex(ssz.encode(value, sedes)) == serialized
    assert ssz.decode(decode_hex(serialized), sedes) == value
