from hypothesis import (
    given,
    strategies as st,
)
import pytest

import ssz
from ssz.sedes import (
    ByteList,
    ByteVector,
    List,
    Vector,
    byte,
    uint8,
)


@pytest.mark.parametrize(
    "value", tuple(bytes([byte_value]) for byte_value in range(256))
)
def test_byte(value):
    expected = ssz.get_hash_tree_root(int.from_bytes(value, byteorder="little"), uint8)
    assert ssz.get_hash_tree_root(value, byte) == expected


@given(st.binary(min_size=1))
def test_byte_vector(value):
    byte_sequence = tuple(bytes([byte_value]) for byte_value in value)
    expected_vector_root = ssz.get_hash_tree_root(
        byte_sequence, Vector(byte, len(value))
    )
    assert ssz.get_hash_tree_root(value, ByteVector(len(value))) == expected_vector_root


@given(st.binary(), st.booleans())
def test_byte_list(value, same_size):
    byte_sequence = tuple(bytes([byte_value]) for byte_value in value)

    if same_size:
        max_length = len(value)
    else:
        max_length = len(value) + 1

    expected_vector_root = ssz.get_hash_tree_root(byte_sequence, List(byte, max_length))
    calculated_vector_root = ssz.get_hash_tree_root(value, ByteList(max_length))
    assert calculated_vector_root == expected_vector_root
