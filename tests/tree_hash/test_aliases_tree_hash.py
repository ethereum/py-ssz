from hypothesis import (
    given,
    strategies as st,
)
import pytest

import ssz
from ssz.sedes import (
    ByteVector,
    List,
    Vector,
    byte,
    byte_list,
    uint8,
)


@pytest.mark.parametrize(
    "value",
    tuple(bytes([byte_value]) for byte_value in range(256)),
)
def test_byte(value):
    expected = ssz.hash_tree_root(int.from_bytes(value, byteorder="little"), uint8)
    assert ssz.hash_tree_root(value, byte) == expected


@given(st.binary())
def test_byte_list(value):
    byte_sequence = tuple(bytes([byte_value]) for byte_value in value)
    max_length = ssz.utils.get_next_power_of_two(len(value))
    assert (
        ssz.hash_tree_root(value, byte_list) ==
        ssz.hash_tree_root(byte_sequence, List(byte, max_length))
    )


@given(st.binary())
def test_byte_vector(value):
    byte_sequence = tuple(bytes([byte_value]) for byte_value in value)
    expected_vector_root = ssz.hash_tree_root(byte_sequence, Vector(byte, len(value)))
    assert ssz.hash_tree_root(value, ByteVector(len(value))) == expected_vector_root
