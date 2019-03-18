from eth_utils import (
    decode_hex,
    encode_hex,
)
import pytest

import ssz
from ssz.sedes import (
    Container,
    List,
    Tuple,
    uint8,
)


@pytest.mark.parametrize(
    ("value", "serialized"),
    (
        ((), "0x00000000"),
        ((0xaa,), "0x01000000aa"),
        ((0xaa, 0xbb, 0xcc), "0x03000000aabbcc"),
        ((0xaa,) * 256, "0x00010000" + "aa" * 256),
        ((0xaa,) * (256**2 - 1), "0xffff0000" + "aa" * (256**2 - 1)),
    ),
)
def test_list(value, serialized):
    sedes = List(uint8)
    assert encode_hex(ssz.encode(value, sedes)) == serialized
    assert ssz.decode(decode_hex(serialized), sedes) == value


@pytest.mark.parametrize(
    ("value", "serialized"),
    (
        ((), "0x"),
        ((0xaa,), "0xaa"),
        ((0xaa, 0xbb, 0xcc), "0xaabbcc"),
    ),
)
def test_tuple_of_static_sized_entries(value, serialized):
    sedes = Tuple(len(value), uint8)
    assert encode_hex(ssz.encode(value, sedes)) == serialized
    assert ssz.decode(decode_hex(serialized), sedes) == value


@pytest.mark.parametrize(
    ("value", "serialized"),
    (
        (((),), "0x0400000000000000"),
        (((0xaa,),), "0x0500000001000000aa"),
        (((0xaa, 0xbb, 0xcc),), "0x0700000003000000aabbcc"),
        (((), (), ()), "0x0c000000000000000000000000000000"),
        (
            ((0xaa,), (0xbb, 0xcc), (0xdd, 0xee, 0xff)),
            "0x1200000001000000aa02000000bbcc03000000ddeeff"
        ),
    )
)
def test_tuple_of_dynamic_sized_entries(value, serialized):
    sedes = Tuple(len(value), List(uint8))
    assert encode_hex(ssz.encode(value, sedes)) == serialized
    assert ssz.decode(decode_hex(serialized), sedes) == value


@pytest.mark.parametrize(
    ("value", "serialized"),
    (
        # ((), "0x"),
        ((0xaa,), "0xaa"),
        ((0xaa, 0xbb, 0xcc), "0xaabbcc"),
    ),
)
def test_container_of_static_sized_fields(value, serialized):
    field_names = tuple(str(index) for index in range(len(value)))
    sedes = Container(tuple((field_name, uint8) for field_name in field_names))
    value_dict = {field_name: field_value for field_name, field_value in zip(field_names, value)}

    assert encode_hex(ssz.encode(value_dict, sedes)) == serialized
    assert ssz.decode(decode_hex(serialized), sedes) == value_dict


@pytest.mark.parametrize(
    ("fields", "value", "serialized"),
    (
        ((List(uint8),), ((),), "0x0400000000000000"),
        ((List(uint8),), ((0xaa, 0xbb),), "0x0600000002000000aabb"),
        ((uint8, List(uint8),), (0xaa, (0xbb, 0xcc)), "0x07000000aa02000000bbcc"),
        ((List(uint8), uint8), ((0xaa, 0xbb), 0xcc), "0x0700000002000000aabbcc"),
        (
            (List(uint8), List(uint8)),
            ((0xaa, 0xbb), (0xcc, 0xdd)),
            "0x0c00000002000000aabb02000000ccdd",
        )
    )
)
def test_container_of_dynamic_sized_fields(fields, value, serialized):
    field_names = tuple(str(index) for index in range(len(fields)))
    sedes = Container(tuple(
        (field_name, field_sedes)
        for field_name, field_sedes in zip(field_names, fields)
    ))
    value_dict = {field_name: field_value for field_name, field_value in zip(field_names, value)}

    assert encode_hex(ssz.encode(value_dict, sedes)) == serialized
    assert ssz.decode(decode_hex(serialized), sedes) == value_dict
